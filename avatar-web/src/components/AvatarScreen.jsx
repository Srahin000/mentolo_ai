import React, { useState, useEffect, useRef } from 'react';
import { createHeyGenSession, getHeyGenAvatars, testHeyGen, closeHeyGenSession, answerHeyGenSession } from '../services/api';
import './AvatarScreen.css';

export default function AvatarScreen() {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [avatars, setAvatars] = useState([]);
  const [selectedAvatarId, setSelectedAvatarId] = useState('Santa_Fireplace_Front_public');
  const [showAvatarSelector, setShowAvatarSelector] = useState(false);
  const [loadingAvatars, setLoadingAvatars] = useState(false);
  
  const websocketRef = useRef(null);
  const videoRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const sessionDataRef = useRef(null);

  useEffect(() => {
    testConnection();
    return () => {
      disconnect();
    };
  }, []);

  const testConnection = async () => {
    try {
      const result = await testHeyGen();
      console.log('HeyGen connection test:', result);
      if (!result.available) {
        setError(`HeyGen not available: ${result.message}`);
      }
    } catch (err) {
      console.error('HeyGen test failed:', err);
    }
  };

  const loadAvatars = async () => {
    try {
      setLoadingAvatars(true);
      const response = await getHeyGenAvatars();
      if (response.success && response.avatars && response.avatars.length > 0) {
        setAvatars(response.avatars);
        // Set first avatar as default if none selected
        if (selectedAvatarId === 'default' && response.avatars[0]) {
          setSelectedAvatarId(response.avatars[0].avatar_id || response.avatars[0].id);
        }
      }
    } catch (err) {
      console.error('Error loading avatars:', err);
      // Don't show error - just use default avatar
    } finally {
      setLoadingAvatars(false);
    }
  };

  const connect = async () => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('=== Creating HeyGen session ===');
      console.log('Avatar ID:', selectedAvatarId);

      // Create HeyGen session with selected avatar (no audio needed)
      const sessionResponse = await createHeyGenSession({
        avatar_id: selectedAvatarId,
        user_id: 'child_user',
      });

      console.log('=== Session response ===');
      console.log('Full response:', JSON.stringify(sessionResponse, null, 2));

      if (!sessionResponse.success) {
        console.error('Session creation failed:', sessionResponse);
        throw new Error(sessionResponse.error || 'Failed to create avatar session');
      }

      const session = sessionResponse.session;
      if (!session) {
        console.error('No session in response:', sessionResponse);
        throw new Error('No session data returned from server');
      }

      console.log('=== Session data ===');
      console.log('Session keys:', Object.keys(session));
      console.log('Full session:', JSON.stringify(session, null, 2));

      // Check for WebRTC SDP offer (new Streaming API format)
      const sdpOffer = session.sdp;
      const realtimeEndpoint = session.realtime_endpoint || session.ws_url || session.rtc_url || session.websocket_url || session.url;
      const livekitUrl = session.livekit_url || session.url;
      const iceServers = session.ice_servers;
      const sessionId = session.session_id;
      const accessToken = session.access_token;
      const livekitAgentToken = session.livekit_agent_token;

      if (sdpOffer) {
        console.log('=== WebRTC SDP Offer received ===');
        console.log('SDP Offer:', sdpOffer);
        console.log('ICE Servers:', iceServers);
        console.log('Session ID:', sessionId);
        console.log('Realtime Endpoint:', realtimeEndpoint);
        console.log('LiveKit URL:', livekitUrl);
        console.log('Access Token:', accessToken ? 'Present' : 'Missing');
        console.log('LiveKit Agent Token:', livekitAgentToken ? 'Present' : 'Missing');
        
        // Store session data for later use
        sessionDataRef.current = session;
        
        // Start WebRTC handshake with LiveKit connection
        await handleWebRTCHandshake(sdpOffer, iceServers, sessionId, livekitUrl, accessToken);
        return;
      }

      // Fallback: Try direct WebSocket connection (old format)
      if (!realtimeEndpoint) {
        console.error('=== NO ENDPOINT FOUND ===');
        console.error('Session response:', sessionResponse);
        console.error('Session object:', session);
        console.error('Available keys:', Object.keys(session));
        throw new Error('No realtime endpoint or WebSocket URL in session response. Check backend logs.');
      }

      console.log('=== Connecting to WebSocket (legacy format) ===');
      console.log('WebSocket URL:', realtimeEndpoint);

      // Connect to WebSocket
      const ws = new WebSocket(realtimeEndpoint);
      websocketRef.current = ws;

      ws.onopen = () => {
        console.log('=== WebSocket connected ===');
        console.log('Ready state:', ws.readyState);
        setIsConnected(true);
        setIsLoading(false);
        // No need to start listening - just show the avatar
      };

      ws.onmessage = (event) => {
        try {
          console.log('=== WebSocket message received ===');
          console.log('Data type:', typeof event.data);
          console.log('Is Blob:', event.data instanceof Blob);
          console.log('Is ArrayBuffer:', event.data instanceof ArrayBuffer);
          
          // Handle both JSON and binary data
          let data;
          if (typeof event.data === 'string') {
            console.log('String data:', event.data);
            data = JSON.parse(event.data);
            console.log('Parsed JSON:', data);
          } else {
            console.log('Binary data received, size:', event.data.byteLength || event.data.size);
            // Binary data might be video stream
            handleVideoStream(event.data);
            return;
          }
          
          console.log('=== Message details ===');
          console.log('Message type:', data.type);
          console.log('Full message:', JSON.stringify(data, null, 2));
          
          if (data.type === 'video' || data.video) {
            console.log('Processing video message');
            // Handle video stream
            handleVideoStream(data.video || data);
          } else if (data.type === 'event' || data.type === 'animation') {
            // Handle avatar events (nodding, expressions, etc.)
            console.log('Avatar event:', data);
          } else if (data.type === 'session') {
            // Session info
            console.log('Session info:', data);
          } else {
            // Unknown message type - log it
            console.log('Unknown message type:', data);
          }
        } catch (err) {
          console.error('=== Error processing message ===');
          console.error('Error:', err);
          console.error('Event data:', event.data);
          // Try to handle as binary video data
          if (event.data instanceof Blob || event.data instanceof ArrayBuffer) {
            console.log('Attempting to handle as binary video');
            handleVideoStream(event.data);
          }
        }
      };

      ws.onerror = (error) => {
        console.error('=== WebSocket error ===');
        console.error('Error object:', error);
        console.error('WebSocket readyState:', ws.readyState);
        console.error('WebSocket URL:', websocket_url);
        setError('WebSocket connection error. Check console for details.');
        setIsConnected(false);
        setIsLoading(false);
      };

      ws.onclose = (event) => {
        console.log('=== WebSocket closed ===');
        console.log('Close code:', event.code);
        console.log('Close reason:', event.reason);
        console.log('Was clean:', event.wasClean);
        setIsConnected(false);
      };

    } catch (err) {
      console.error('Error connecting:', err);
      setError(err.message || 'Oops! Something went wrong. Try again!');
      setIsLoading(false);
    }
  };

  const handleWebRTCHandshake = async (sdpOffer, iceServers, sessionId, livekitUrl, accessToken) => {
    try {
      console.log('=== Starting WebRTC handshake ===');
      
      // Convert ICE servers format if needed
      const rtcIceServers = iceServers ? iceServers.map(server => {
        const config = { urls: server.urls || [server.url] };
        if (server.username) config.username = server.username;
        if (server.credential) config.credential = server.credential;
        return config;
      }) : [];
      
      console.log('ICE servers for RTCPeerConnection:', rtcIceServers);
      
      // Create RTCPeerConnection
      const pc = new RTCPeerConnection({
        iceServers: rtcIceServers.length > 0 ? rtcIceServers : [
          { urls: 'stun:stun.l.google.com:19302' }
        ]
      });
      
      peerConnectionRef.current = pc;
      
      // Handle incoming video/audio tracks
      pc.ontrack = (event) => {
        console.log('=== WebRTC track received ===');
        console.log('Track kind:', event.track.kind);
        console.log('Stream:', event.streams[0]);
        console.log('Track state:', event.track.readyState);
        
        if (event.track.kind === 'video' && videoRef.current) {
          const stream = event.streams[0];
          console.log('Setting video stream to element...');
          console.log('Stream tracks:', stream.getTracks().map(t => ({ kind: t.kind, id: t.id, enabled: t.enabled, readyState: t.readyState })));
          
          // Clear any existing stream first
          if (videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
          }
          
          videoRef.current.srcObject = stream;
          
          // Wait for track to be ready
          event.track.onended = () => {
            console.log('Video track ended');
            setIsConnected(false);
          };
          
          event.track.onmute = () => {
            console.log('Video track muted');
          };
          
          event.track.onunmute = () => {
            console.log('Video track unmuted');
          };
          
          // Check if track is already ready
          if (event.track.readyState === 'live') {
            console.log('✅ Track is live, attempting to play...');
          } else {
            console.log('Track readyState:', event.track.readyState);
            event.track.onstart = () => {
              console.log('✅ Track started');
            };
          }
          
          // Force video element to be visible and ready
          videoRef.current.muted = true; // Required for autoplay
          videoRef.current.playsInline = true;
          
          // Try to play video with retry logic
          const tryPlay = async () => {
            try {
              // Show video element
              if (videoRef.current) {
                videoRef.current.style.display = 'block';
              }
              
              await videoRef.current.play();
              console.log('✅ Video playing');
              setIsConnected(true);
              setIsLoading(false);
              setError(null);
            } catch (err) {
              console.error('Video play error:', err);
              console.error('Video element state:', {
                paused: videoRef.current.paused,
                readyState: videoRef.current.readyState,
                srcObject: !!videoRef.current.srcObject,
                muted: videoRef.current.muted
              });
              
              // Retry after a short delay
              setTimeout(() => {
                console.log('Retrying video play...');
                if (videoRef.current) {
                  videoRef.current.play().then(() => {
                    console.log('✅ Video playing (retry successful)');
                    setIsConnected(true);
                    setIsLoading(false);
                    setError(null);
                  }).catch(retryErr => {
                    console.error('Video play retry failed:', retryErr);
                    setError('Could not play video. Check browser permissions.');
                    setIsLoading(false);
                  });
                }
              }, 500);
            }
          };
          
          // Wait for video element to be ready
          if (videoRef.current.readyState >= 2) {
            tryPlay();
          } else {
            const onReady = () => {
              console.log('Video ready to play');
              tryPlay();
            };
            
            videoRef.current.onloadedmetadata = onReady;
            videoRef.current.oncanplay = onReady;
            videoRef.current.onloadeddata = onReady;
            
            // Also try immediately in case it's already ready
            setTimeout(tryPlay, 100);
          }
        }
      };
      
      // Handle ICE connection state changes
      pc.oniceconnectionstatechange = () => {
        const state = pc.iceConnectionState;
        console.log('ICE connection state:', state);
        
        if (state === 'connected' || state === 'completed') {
          console.log('✅ ICE connection established!');
          setIsConnected(true);
          setIsLoading(false);
          setError(null);
        } else if (state === 'failed') {
          console.error('❌ ICE connection failed');
          setError('WebRTC connection failed. Check network/firewall settings.');
          setIsLoading(false);
        } else if (state === 'disconnected') {
          console.warn('⚠️  ICE connection disconnected');
          setError('WebRTC connection disconnected');
          setIsLoading(false);
        } else if (state === 'checking') {
          console.log('🔄 ICE connection checking...');
          // Keep loading state
        }
      };
      
      // Handle ICE gathering state
      pc.onicegatheringstatechange = () => {
        console.log('ICE gathering state:', pc.iceGatheringState);
      };
      
      // Set remote description (HeyGen's offer) FIRST
      console.log('Setting remote description with offer...');
      await pc.setRemoteDescription(new RTCSessionDescription(sdpOffer));
      console.log('✅ Remote description set');
      
      // Create answer
      console.log('Creating answer...');
      const answer = await pc.createAnswer();
      console.log('✅ Answer created:', answer);
      
      // Set local description (this starts ICE gathering)
      await pc.setLocalDescription(answer);
      console.log('✅ Local description set');
      
      // CRITICAL: Wait for ICE gathering to complete BEFORE sending answer
      console.log('⏳ Waiting for ICE gathering to complete...');
      
      // Wait for ICE gathering to complete, then send answer
      const sendAnswerWhenReady = () => {
        return new Promise((resolve, reject) => {
          // Check if already complete
          if (pc.iceGatheringState === 'complete') {
            console.log('✅ ICE gathering already complete');
            resolve();
            return;
          }
          
          // Wait for ICE gathering to complete
          pc.onicegatheringstatechange = async () => {
            console.log('ICE gathering state:', pc.iceGatheringState);
            
            if (pc.iceGatheringState === 'complete') {
              console.log('✅ ICE gathering complete - ready to send answer');
              resolve();
            }
          };
          
          // Also check onicecandidate null event (indicates completion)
          pc.onicecandidate = (event) => {
            if (event.candidate) {
              console.log('ICE candidate:', event.candidate);
            } else {
              console.log('✅ ICE gathering complete (null candidate)');
              if (pc.iceGatheringState === 'complete') {
                resolve();
              }
            }
          };
          
          // Timeout after 10 seconds
          setTimeout(() => {
            if (pc.iceGatheringState !== 'complete') {
              console.warn('⚠️  ICE gathering timeout, sending answer anyway');
              resolve();
            }
          }, 10000);
        });
      };
      
      // Wait for ICE gathering, then send answer
      await sendAnswerWhenReady();
      
      // Now send the answer to HeyGen
      console.log('📤 Sending SDP answer to HeyGen...');
      const answerPayload = {
        type: pc.localDescription.type,
        sdp: pc.localDescription.sdp
      };
      
      try {
        const answerResponse = await answerHeyGenSession(sessionId, answerPayload);
        console.log('=== Answer response ===');
        console.log(answerResponse);
        
        if (answerResponse.success && answerResponse.message === 'success') {
          console.log('✅ SDP answer sent successfully!');
          console.log('✅ Waiting for video track via ontrack event...');
        } else {
          console.warn('⚠️  Unexpected answer response:', answerResponse);
        }
      } catch (answerErr) {
        console.error('❌ Error sending SDP answer:', answerErr);
        setError(`Failed to send SDP answer: ${answerErr.message}`);
        setIsLoading(false);
        return;
      }
      
      // Monitor connection state
      const checkConnection = setInterval(() => {
        if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
          clearInterval(checkConnection);
        } else if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'disconnected') {
          clearInterval(checkConnection);
        }
      }, 1000);
      
      // Clear interval after 30 seconds
      setTimeout(() => {
        clearInterval(checkConnection);
      }, 30000);
      
    } catch (err) {
      console.error('=== WebRTC handshake error ===');
      console.error('Error:', err);
      setError(`WebRTC error: ${err.message}`);
      setIsLoading(false);
      
      // Cleanup
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
    }
  };

  const disconnect = async () => {
    console.log('=== Disconnecting ===');
    
    // Close session via API if we have a session ID
    if (sessionDataRef.current && sessionDataRef.current.session_id) {
      try {
        console.log('Closing session via API...');
        await closeHeyGenSession(sessionDataRef.current.session_id);
        console.log('✅ Session closed via API');
      } catch (err) {
        console.warn('Could not close session via API (may already be closed):', err);
      }
    }
    
    // Close WebSocket if open
    if (websocketRef.current) {
      console.log('Closing WebSocket...');
      websocketRef.current.close();
      websocketRef.current = null;
    }
    
    // Close WebRTC peer connection if open
    if (peerConnectionRef.current) {
      console.log('Closing WebRTC peer connection...');
      try {
        // Close all tracks first
        peerConnectionRef.current.getSenders().forEach(sender => {
          if (sender.track) {
            sender.track.stop();
          }
        });
        peerConnectionRef.current.getReceivers().forEach(receiver => {
          if (receiver.track) {
            receiver.track.stop();
          }
        });
        peerConnectionRef.current.close();
      } catch (err) {
        console.error('Error closing peer connection:', err);
      }
      peerConnectionRef.current = null;
    }
    
    // Stop video tracks
    if (videoRef.current && videoRef.current.srcObject) {
      console.log('Stopping video tracks...');
      videoRef.current.srcObject.getTracks().forEach(track => {
        track.stop();
        console.log(`Stopped ${track.kind} track`);
      });
      videoRef.current.srcObject = null;
    }
    
    // Clear session data
    sessionDataRef.current = null;
    
    setIsConnected(false);
    console.log('✅ Disconnected');
  };

  const handleVideoStream = (videoData) => {
    console.log('=== Handling video stream ===');
    console.log('Video data type:', typeof videoData);
    console.log('Is Blob:', videoData instanceof Blob);
    console.log('Is ArrayBuffer:', videoData instanceof ArrayBuffer);
    
    // Handle video stream from HeyGen
    if (!videoRef.current) {
      console.error('Video ref not available');
      return;
    }
    
    try {
      if (videoData instanceof Blob) {
        console.log('Processing Blob, size:', videoData.size, 'type:', videoData.type);
        const url = URL.createObjectURL(videoData);
        console.log('Created object URL:', url);
        videoRef.current.src = url;
        videoRef.current.play().then(() => {
          console.log('Video playing successfully');
        }).catch(err => {
          console.error('Video play error:', err);
        });
      } else if (videoData instanceof ArrayBuffer) {
        console.log('Processing ArrayBuffer, size:', videoData.byteLength);
        const blob = new Blob([videoData], { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        console.log('Created object URL from ArrayBuffer:', url);
        videoRef.current.src = url;
        videoRef.current.play().then(() => {
          console.log('Video playing successfully');
        }).catch(err => {
          console.error('Video play error:', err);
        });
      } else if (typeof videoData === 'string') {
        console.log('Processing string video data, length:', videoData.length);
        // Base64 or URL string
        if (videoData.startsWith('data:')) {
          videoRef.current.src = videoData;
        } else if (videoData.startsWith('http')) {
          videoRef.current.src = videoData;
        } else {
          videoRef.current.src = `data:video/webm;base64,${videoData}`;
        }
        videoRef.current.play().then(() => {
          console.log('Video playing successfully');
        }).catch(err => {
          console.error('Video play error:', err);
        });
      } else {
        console.error('Unknown video data type:', typeof videoData);
        console.error('Video data:', videoData);
      }
    } catch (err) {
      console.error('=== Error handling video stream ===');
      console.error('Error:', err);
      console.error('Video data:', videoData);
    }
  };

  // Audio functions removed - not needed for visual-only avatar

  const getSelectedAvatarName = () => {
    const selected = avatars.find(a => (a.avatar_id || a.id) === selectedAvatarId);
    if (selected) {
      return selected.name || selected.avatar_id || selected.id;
    }
    // If not found in avatars list, show the ID (truncated if long)
    if (selectedAvatarId && selectedAvatarId !== 'default') {
      return selectedAvatarId.length > 20 
        ? `${selectedAvatarId.substring(0, 20)}...` 
        : selectedAvatarId;
    }
    return 'Default Avatar';
  };

  return (
    <div className="avatar-screen">
      <div className="avatar-header">
        <h1>Your AI Friend</h1>
        <p>Watch your avatar come to life!</p>
        {!isConnected && (
          <button 
            className="btn-select-avatar"
            onClick={() => {
              if (!showAvatarSelector && avatars.length === 0) {
                // Only load avatars when user clicks to choose
                loadAvatars();
              }
              setShowAvatarSelector(!showAvatarSelector);
            }}
            disabled={loadingAvatars}
          >
            {loadingAvatars ? 'Loading...' : `Choose Avatar: ${getSelectedAvatarName()}`}
          </button>
        )}
      </div>

      {showAvatarSelector && !isConnected && (
        <div className="avatar-selector">
          <h3>Choose Your Avatar</h3>
          
          {/* Manual Avatar ID Input */}
          <div className="custom-avatar-input">
            <label>Enter your Avatar ID:</label>
            <input
              type="text"
              value={selectedAvatarId === 'default' ? '' : selectedAvatarId}
              onChange={(e) => {
                const value = e.target.value.trim();
                if (value) {
                  setSelectedAvatarId(value);
                } else {
                  setSelectedAvatarId('default');
                }
              }}
              placeholder="e.g., 04532556f6ca4d1cae1d3796cae664b6"
              className="avatar-id-input"
            />
            <p className="input-hint">Paste your HeyGen avatar ID here</p>
          </div>
          
          {/* Avatar Grid from API */}
          {avatars.length > 0 && (
            <>
              <div className="avatar-divider">
                <span>Or choose from available avatars:</span>
              </div>
              <div className="avatar-grid">
                {avatars.map((avatar) => {
                  const avatarId = avatar.avatar_id || avatar.id;
                  const avatarName = avatar.name || avatarId;
                  const isSelected = avatarId === selectedAvatarId;
                  
                  return (
                    <button
                      key={avatarId}
                      className={`avatar-option ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        setSelectedAvatarId(avatarId);
                        setShowAvatarSelector(false);
                      }}
                    >
                      <div className="avatar-option-emoji">
                        {avatar.thumbnail_url ? (
                          <img src={avatar.thumbnail_url} alt={avatarName} />
                        ) : (
                          <span>👤</span>
                        )}
                      </div>
                      <p>{avatarName}</p>
                      {isSelected && <span className="checkmark">✓</span>}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}

      <div className="avatar-video-container">
        {/* Always render video element so we can set stream when tracks arrive */}
        <video 
          ref={videoRef}
          autoPlay
          playsInline
          className="avatar-video"
          muted
          style={{ display: isConnected ? 'block' : 'none' }}
        />
        
        {!isConnected && (
          <div className="avatar-placeholder">
            <div className="avatar-emoji">🤖</div>
            <p>{isLoading ? 'Getting ready...' : 'Tap the button to start!'}</p>
          </div>
        )}

        {isLoading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Connecting...</p>
          </div>
        )}

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}
      </div>

      <div className="avatar-controls">
        {!isConnected ? (
          <button 
            className="btn-connect"
            onClick={connect}
            disabled={isLoading}
          >
            {isLoading ? 'Connecting...' : 'Start Avatar!'}
          </button>
        ) : (
          <button 
            className="btn-disconnect"
            onClick={disconnect}
          >
            Disconnect 👋
          </button>
        )}
      </div>
    </div>
  );
}

