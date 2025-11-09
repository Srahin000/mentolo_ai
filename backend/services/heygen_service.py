"""
HeyGen Realtime Avatar Service
Integrates HeyGen's Realtime Avatar API for interactive video conversations
"""

import os
import logging
import requests
import uuid
from typing import Dict, Optional, List
from time import time

logger = logging.getLogger(__name__)


class HeyGenService:
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        self.base_url = 'https://api.heygen.com/v2'
        self.is_available_flag = self.api_key is not None
        self._avatar_cache = None
        self._avatar_cache_time = 0
        self._cache_ttl = 300  # Cache avatars for 5 minutes
        
        if self.is_available_flag:
            logger.info("HeyGen service initialized")
        else:
            logger.warning("HeyGen API key not found - service unavailable")
    
    def is_available(self):
        """Check if HeyGen service is available"""
        return self.is_available_flag
    
    def create_realtime_session(self, avatar_id: str, voice_id: str = None) -> Dict:
        """
        Create a new realtime avatar session
        
        Args:
            avatar_id: HeyGen avatar ID
            voice_id: Optional voice ID (uses default if not provided)
        
        Returns:
            Dict with session_id and connection details
        """
        if not self.is_available():
            raise Exception("HeyGen API key not configured")
        
        # Verify avatar is interactive before creating session
        try:
            avatar_info = self.check_avatar_exists(avatar_id)
            logger.info(f"Avatar verified as interactive: {avatar_info.get('name', 'Unknown')}")
        except Exception as check_error:
            # If check fails, log but continue - API will give better error
            logger.warning(f"Avatar check failed: {check_error}")
            logger.warning(f"Will attempt session creation anyway - API will provide specific error")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        base_url = "https://api.heygen.com/v1"
        
        # Create a new streaming session (HeyGen Streaming API - WebRTC-based)
        # This returns an SDP offer that the client must answer
        create_url = f"{base_url}/streaming.new"
        
        # Build payload for session creation
        create_payload = {
            'avatar_id': avatar_id,
            'config': {
                'quality': 'high',
                'resolution': '720p'
            }
        }
        
        if voice_id:
            create_payload['voice_id'] = voice_id
        
        logger.info(f"=== Creating HeyGen streaming session ===")
        logger.info(f"URL: {create_url}")
        logger.info(f"Avatar ID: {avatar_id}")
        logger.info(f"Voice ID: {voice_id or 'default'}")
        logger.info(f"Payload: {create_payload}")
        
        try:
            # Create the streaming session - returns SDP offer
            create_response = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
            
            logger.info(f"Response status: {create_response.status_code}")
            
            if create_response.status_code != 200:
                logger.error(f"Failed to create session: {create_response.status_code}")
                logger.error(f"Response text: {create_response.text}")
                
                # Check for specific error codes
                try:
                    error_data = create_response.json()
                    error_code = error_data.get('code')
                    error_message = error_data.get('message', '')
                    
                    if error_code == 10004:
                        # Concurrent limit reached - free plan only allows 1 concurrent session
                        logger.warning("⚠️  Concurrent session limit reached")
                        logger.warning("Free plan allows only 1 concurrent session")
                        logger.warning("Please close any existing sessions or wait for them to expire")
                        raise Exception(
                            "Concurrent session limit reached. The free plan allows only 1 concurrent session. "
                            "Please close any existing sessions or wait a few minutes and try again."
                        )
                except:
                    pass
                
                create_response.raise_for_status()
            
            create_result = create_response.json()
            logger.info(f"=== Streaming session creation response ===")
            logger.info(f"{create_result}")
            
            # Extract data from response (HeyGen returns data wrapper)
            if 'data' in create_result:
                session_data = create_result['data']
            else:
                session_data = create_result
            
            session_id = session_data.get('session_id')
            if not session_id:
                raise Exception("No session_id returned from session creation")
            
            # Extract all the important fields from the response
            sdp_offer = session_data.get('sdp')  # WebRTC offer SDP
            access_token = session_data.get('access_token')
            realtime_endpoint = session_data.get('realtime_endpoint')  # WebSocket endpoint
            livekit_agent_token = session_data.get('livekit_agent_token')
            livekit_url = session_data.get('url')  # LiveKit WebSocket URL
            # HeyGen returns ice_servers2, not ice_servers
            ice_servers = session_data.get('ice_servers2') or session_data.get('ice_servers')  # TURN/STUN servers
            
            logger.info(f"✅ Streaming session created with ID: {session_id}")
            logger.info(f"SDP offer present: {sdp_offer is not None}")
            logger.info(f"Realtime endpoint: {realtime_endpoint}")
            logger.info(f"LiveKit URL: {livekit_url}")
            logger.info(f"Access token present: {access_token is not None}")
            logger.info(f"ICE servers present: {ice_servers is not None}")
            if ice_servers:
                logger.info(f"ICE servers count: {len(ice_servers) if isinstance(ice_servers, list) else 'N/A'}")
            
            # Return all necessary data for WebRTC handshake
            # Client will need to:
            # 1. Create RTCPeerConnection with ICE servers
            # 2. Set remote description with the SDP offer
            # 3. Create answer SDP
            # 4. Set local description with the answer (this completes the handshake automatically)
            # 5. Video will arrive via ontrack event - no need to call /streaming.answer
            final_session_data = {
                'session_id': session_id,
                'sdp': sdp_offer,  # WebRTC offer - client must create answer
                'access_token': access_token,
                'realtime_endpoint': realtime_endpoint,  # WebRTC signaling endpoint
                'livekit_url': livekit_url,  # LiveKit WebSocket URL
                'livekit_agent_token': livekit_agent_token,
                'ice_servers': ice_servers,  # TURN/STUN servers for WebRTC
                # Legacy aliases for frontend compatibility
                'rtc_url': realtime_endpoint or livekit_url,
                'websocket_url': realtime_endpoint or livekit_url,
                'ws_url': realtime_endpoint or livekit_url,
                'url': realtime_endpoint or livekit_url,
            }
            
            logger.info(f"✅ Session data prepared for WebRTC handshake")
            logger.info(f"Realtime endpoint: {realtime_endpoint or 'NOT FOUND'}")
            logger.info(f"Full session data keys: {list(final_session_data.keys())}")
            
            return final_session_data
                
        except requests.exceptions.RequestException as e:
            logger.error(f"=== Error creating HeyGen session ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
                logger.error(f"Response text: {e.response.text}")
                try:
                    error_detail = e.response.json()
                    logger.error(f"Response JSON: {error_detail}")
                    error_msg = error_detail.get('message') or error_detail.get('error') or str(error_detail)
                    raise Exception(f"HeyGen API error ({e.response.status_code}): {error_msg}")
                except:
                    raise Exception(f"HeyGen API error ({e.response.status_code}): {e.response.text}")
            raise Exception(f"HeyGen connection error: {str(e)}")
    
    def close_session(self, session_id: str) -> bool:
        """
        Close/terminate a HeyGen streaming session
        
        Args:
            session_id: The session ID to close
        
        Returns:
            True if session was closed successfully, False otherwise
        """
        if not self.is_available():
            logger.warning("HeyGen API key not configured - cannot close session")
            return False
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Try streaming.stop endpoint
        stop_url = "https://api.heygen.com/v1/streaming.stop"
        
        payload = {
            'session_id': session_id
        }
        
        try:
            logger.info(f"=== Closing HeyGen session ===")
            logger.info(f"Session ID: {session_id}")
            
            response = requests.post(stop_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Session closed successfully")
                return True
            else:
                logger.warning(f"Session close response: {response.status_code}")
                logger.warning(f"Response: {response.text}")
                # Don't raise - session might already be closed
                return False
                
        except Exception as e:
            logger.warning(f"Error closing session (may already be closed): {e}")
            return False
    
    def get_avatar_list(self, use_cache: bool = False, interactive_only: bool = False) -> List[Dict]:
        """Get list of available avatars - NO FALLBACKS"""
        if not self.is_available():
            logger.error("HeyGen service not available")
            raise Exception("HeyGen API key not configured")
        
        # Use correct endpoint with Bearer auth
        url = "https://api.heygen.com/v1/avatar.list"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"=== Fetching avatar list ===")
        logger.info(f"URL: {url}")
        logger.info(f"Interactive only: {interactive_only}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Handle different response formats
            if 'data' in result:
                if isinstance(result['data'], list):
                    avatars = result['data']
                else:
                    avatars = result['data'].get('avatars', [])
            elif 'avatars' in result:
                avatars = result['avatars']
            elif isinstance(result, list):
                avatars = result
            else:
                logger.error(f"Unexpected response format: {result}")
                avatars = []
            
            # Filter for interactive avatars if requested
            if interactive_only:
                interactive_avatars = [a for a in avatars if a.get('is_interactive', False)]
                logger.info(f"Retrieved {len(interactive_avatars)} interactive avatars out of {len(avatars)} total")
                return interactive_avatars
            
            # Log interactive avatar count
            interactive_count = sum(1 for a in avatars if a.get('is_interactive', False))
            logger.info(f"Retrieved {len(avatars)} avatars from HeyGen ({interactive_count} interactive)")
            
            return avatars
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching avatars (request took >30s): {e}")
            raise Exception(f"Timeout fetching avatars: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching avatars: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            raise Exception(f"Error fetching avatars: {str(e)}")
    
    def get_interactive_avatars(self) -> List[Dict]:
        """Get only interactive avatars (required for streaming API)"""
        return self.get_avatar_list(interactive_only=True)
    
    def check_avatar_exists(self, avatar_id: str) -> Dict:
        """
        Check if a specific avatar exists and get its details
        Returns avatar details if found, raises exception if not
        """
        if not self.is_available():
            raise Exception("HeyGen API key not configured")
        
        logger.info(f"=== Checking avatar existence ===")
        logger.info(f"Avatar ID: {avatar_id}")
        
        # First, try to get all avatars and find this one
        avatars = self.get_avatar_list(use_cache=False)
        
        found_avatar = None
        for avatar in avatars:
            check_id = avatar.get('avatar_id') or avatar.get('id') or avatar.get('avatarId')
            if check_id == avatar_id:
                found_avatar = avatar
                logger.info(f"✅ Found avatar in list")
                logger.info(f"Avatar details: {avatar}")
                break
        
        if not found_avatar:
            # Try alternative ID fields
            logger.warning(f"Avatar not found with standard ID fields, checking all fields...")
            for avatar in avatars:
                # Check all possible ID fields
                all_ids = [
                    avatar.get('avatar_id'),
                    avatar.get('id'),
                    avatar.get('avatarId'),
                    avatar.get('avatar_id_str'),
                    str(avatar.get('avatar_id', '')),
                    str(avatar.get('id', '')),
                ]
                if avatar_id in all_ids:
                    found_avatar = avatar
                    logger.info(f"✅ Found avatar with alternative ID field")
                    logger.info(f"Avatar details: {avatar}")
                    break
        
        if not found_avatar:
            logger.error(f"❌ Avatar ID {avatar_id} NOT FOUND")
            logger.error(f"Searched through {len(avatars)} avatars")
            logger.error(f"Sample avatar structure: {avatars[0] if avatars else 'No avatars'}")
            
            # Check if it might be a group_id instead
            logger.warning(f"Note: This might be a group_id, not an avatar_id")
            logger.warning(f"Group IDs are different from avatar IDs in HeyGen")
            
            raise Exception(
                f"Avatar ID '{avatar_id}' not found in your HeyGen account. "
                f"This might be a group_id instead of an avatar_id. "
                f"Please check your HeyGen Studio to get the correct avatar_id."
            )
        
        # Check if avatar is interactive (required for streaming API)
        is_interactive = found_avatar.get('is_interactive', False)
        if not is_interactive:
            logger.warning(f"⚠️  Avatar '{avatar_id}' is NOT interactive")
            logger.warning(f"⚠️  Only interactive avatars work with the Streaming API")
            raise Exception(
                f"Avatar '{avatar_id}' is not an interactive avatar. "
                f"Only interactive avatars work with the Streaming API. "
                f"Please use an interactive avatar (check with /api/heygen/avatars/interactive)."
            )
        
        logger.info(f"✅ Avatar is interactive - compatible with Streaming API")
        
        # Check avatar type
        avatar_type = found_avatar.get('type') or found_avatar.get('avatar_type') or found_avatar.get('kind')
        if avatar_type:
            logger.info(f"Avatar type: {avatar_type}")
        
        # Check status
        status = found_avatar.get('status') or found_avatar.get('state')
        if status:
            logger.info(f"Avatar status: {status}")
            if status.lower() not in ['ready', 'active', 'completed', 'available']:
                logger.warning(f"⚠️  Avatar status is '{status}', might not be ready")
        
        return found_avatar
    
    def get_voice_list(self) -> List[Dict]:
        """Get list of available voices"""
        if not self.is_available():
            return []
        
        # Try different endpoint formats
        url = f"{self.base_url}/voices"
        headers = {
            'X-API-KEY': self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if 'data' in result:
                if isinstance(result['data'], list):
                    voices = result['data']
                else:
                    voices = result['data'].get('voices', [])
            elif 'voices' in result:
                voices = result['voices']
            elif isinstance(result, list):
                voices = result
            else:
                voices = []
            
            logger.info(f"Retrieved {len(voices)} voices from HeyGen")
            return voices
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching voices: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response text: {e.response.text}")
            return []

