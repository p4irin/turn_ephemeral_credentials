import unittest
import os
from dotenv import load_dotenv
import aioice
from turn_ephemeral_credentials import generate


load_dotenv()


class TestTurnEphemeralCredentials(unittest.IsolatedAsyncioTestCase):

    class _TestData:
        turn_server: str = os.getenv('TURN_SERVER')
        turn_server_port: int = os.getenv('TURN_SERVER_PORT')
        turn_ssl: bool = bool(os.getenv('TURN_SSL'))
        turn_transport: str = os.getenv('TURN_TRANSPORT')
        use_ipv4: bool = bool(os.getenv('USE_IPV4'))
        use_ipv6: bool = bool(os.getenv('USE_IPV6'))
        shared_secret: str = os.getenv('SHARED_SECRET')

    @classmethod
    def setUpClass(cls) -> None:
        credentials = generate(shared_secret=cls._TestData.shared_secret)
        cls.connection = aioice.Connection(
            ice_controlling=True,
            turn_server=(
                cls._TestData.turn_server, 
                cls._TestData.turn_server_port
            ),
            turn_username=credentials['turn_username'],
            turn_password=credentials['turn_password'],
            turn_ssl=cls._TestData.turn_ssl,
            turn_transport=cls._TestData.turn_transport,
            use_ipv4=cls._TestData.use_ipv4,
            use_ipv6=cls._TestData.use_ipv6
        )
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    async def test_credentials(self):
        """
        If we can gather candidates, we passed authentication.
        Turn relay allocation is also tested.
        """
        try:
            await self.connection.gather_candidates()
        except aioice.stun.TransactionFailed:
            self.fail('401 - Unauthorized')

        has_relay = False
        for candidate in self.connection.local_candidates:
            sdp = candidate.to_sdp().lower()
            if 'relay' in sdp:
                has_relay = True
                break
        self.assertTrue(has_relay)
