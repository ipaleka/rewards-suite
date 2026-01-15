"""Testing module for :py:mod:`updaters.telegram` module."""

import asyncio
from pathlib import Path

import pytest
from telethon.errors import SessionPasswordNeededError

import updaters.telegram
from updaters.base import BaseUpdater
from updaters.telegram import TelegramUpdater


class TestUpdatersTelegramTelegramUpdater:
    """Testing class for :py:mod:`updaters.telegram.TelegramUpdater` class."""

    def test_updaters_telegram_telegramupdater_is_subclass_of_baseupdater(self):
        assert issubclass(TelegramUpdater, BaseUpdater)

    # __init__
    def test_updaters_telegram_telegramtracker_init_functionality(self, mocker):
        telegram_config = {
            "api_id": "test_api_id",
            "api_hash": "test_api_hash",
            "session_name": "test_session",
            "bot_username": "test_bot",
            "poll_interval": 15,
        }
        mock_init = mocker.patch("updaters.telegram.BaseUpdater.__init__")
        mock_config = mocker.patch(
            "updaters.telegram.telegram_config", return_value=telegram_config
        )
        mock_client = mocker.patch("updaters.telegram.TelegramClient")
        session_path = (
            Path(updaters.telegram.__file__).resolve().parent.parent
            / "fixtures"
            / "test_session.session"
        )
        instance = TelegramUpdater(1, 2, foo="bar")
        mock_init.assert_called_once_with(1, 2, foo="bar")
        mock_config.assert_called_once_with()
        mock_client.assert_called_once_with(
            session=session_path,
            api_id="test_api_id",
            api_hash="test_api_hash",
        )
        assert instance.client == mock_client.return_value
        assert instance._is_connected is False

    # updaters/tests/test_telegram.py (continued)

    # _add_reply_async
    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_add_reply_async_success(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock the required methods
        mock_ensure_connected = mocker.AsyncMock()
        mock_parse_message_url = mocker.Mock(return_value=(-123456, 789))
        mock_send_message = mocker.AsyncMock()
        # Patch instance methods
        instance._ensure_connected = mock_ensure_connected
        instance._parse_message_url = mock_parse_message_url
        instance.client.send_message = mock_send_message
        # Mock logger to verify it's called
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = await instance._add_reply_async("test_url", "Test reply text")
        # Assertions
        assert result is True
        mock_ensure_connected.assert_called_once()
        mock_parse_message_url.assert_called_once_with("test_url")
        mock_send_message.assert_called_once_with(
            entity=-123456, message="Test reply text", reply_to=789
        )
        mock_logger.info.assert_called_once_with("Added reply to message: test_url")
        mock_logger.error.assert_not_called()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_add_reply_async_positive_chat_id(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock methods
        mock_ensure_connected = mocker.AsyncMock()
        mock_parse_message_url = mocker.Mock(return_value=(123456, 789))
        mock_send_message = mocker.AsyncMock()
        instance._ensure_connected = mock_ensure_connected
        instance._parse_message_url = mock_parse_message_url
        instance.client.send_message = mock_send_message
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = await instance._add_reply_async("test_url", "Test reply")
        # Assertions
        assert result is True
        mock_parse_message_url.assert_called_once_with("test_url")
        mock_send_message.assert_called_once_with(
            entity=123456, message="Test reply", reply_to=789
        )
        mock_logger.info.assert_called_once_with("Added reply to message: test_url")

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_add_reply_async_connection_error(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock _ensure_connected to raise an exception
        mock_ensure_connected = mocker.AsyncMock(
            side_effect=Exception("Connection failed")
        )
        instance._ensure_connected = mock_ensure_connected
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = await instance._add_reply_async("test_url", "Test reply")
        # Assertions
        assert result is False
        mock_ensure_connected.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Error adding reply to test_url: Connection failed"
        )
        mock_logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_add_reply_async_send_message_error(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock methods
        mock_ensure_connected = mocker.AsyncMock()
        mock_parse_message_url = mocker.Mock(return_value=(-123456, 789))
        mock_send_message = mocker.AsyncMock(
            side_effect=Exception("Failed to send message")
        )
        instance._ensure_connected = mock_ensure_connected
        instance._parse_message_url = mock_parse_message_url
        instance.client.send_message = mock_send_message
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = await instance._add_reply_async("test_url", "Test reply")
        # Assertions
        assert result is False
        mock_ensure_connected.assert_called_once()
        mock_parse_message_url.assert_called_once_with("test_url")
        mock_send_message.assert_called_once_with(
            entity=-123456, message="Test reply", reply_to=789
        )
        mock_logger.error.assert_called_once_with(
            "Error adding reply to test_url: Failed to send message"
        )
        mock_logger.info.assert_not_called()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_add_reply_async_empty_text(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock methods
        mock_ensure_connected = mocker.AsyncMock()
        mock_parse_message_url = mocker.Mock(return_value=(-123456, 789))
        mock_send_message = mocker.AsyncMock()
        instance._ensure_connected = mock_ensure_connected
        instance._parse_message_url = mock_parse_message_url
        instance.client.send_message = mock_send_message
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method with empty text
        result = await instance._add_reply_async("test_url", "")
        # Assertions
        assert result is True
        mock_send_message.assert_called_once_with(
            entity=-123456, message="", reply_to=789
        )
        mock_logger.info.assert_called_once_with("Added reply to message: test_url")

    # # _ensure_connected
    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_success(
        self, mocker
    ):
        # 1. Patch the TelegramClient class and capture its mock return value
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        # 2. Get the mock instance assigned to instance.client
        mock_client_instance = mock_client_class.return_value
        # 3. Setup and assign the dedicated AsyncMock for the methods
        mock_connect = mocker.AsyncMock()
        mock_is_user_authorized = mocker.AsyncMock(return_value=True)
        mock_client_instance.connect = mock_connect
        mock_client_instance.is_user_authorized = mock_is_user_authorized
        instance._is_connected = False
        await instance._ensure_connected()
        # Assertions
        mock_connect.assert_called_once()
        mock_is_user_authorized.assert_called_once()
        assert instance._is_connected is True

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_password_error(
        self, mocker
    ):
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.logger = mocker.MagicMock()
        # Get the mock instance
        mock_client_instance = mock_client_class.return_value
        # Setup and assign the dedicated AsyncMock for methods
        mock_connect = mocker.AsyncMock()
        mock_is_user_authorized = mocker.AsyncMock(return_value=False)
        mock_send_code_request = mocker.AsyncMock()
        # First sign_in raises SessionPasswordNeededError, second succeeds
        mock_sign_in = mocker.AsyncMock()
        mock_sign_in.side_effect = [
            SessionPasswordNeededError("Need password"),  # First call
            None,  # Second call with password
        ]
        mock_client_instance.connect = mock_connect
        mock_client_instance.is_user_authorized = mock_is_user_authorized
        mock_client_instance.send_code_request = mock_send_code_request
        mock_client_instance.sign_in = mock_sign_in
        instance._is_connected = False
        # Mock input to avoid hanging - need two inputs (phone/code) then password
        input_calls = ["123456789", "123456", "2fapassword"]
        mocker.patch("builtins.input", side_effect=input_calls)
        await instance._ensure_connected()
        # Assertions
        mock_connect.assert_called_once()
        mock_is_user_authorized.assert_called_once()
        mock_send_code_request.assert_called_once()
        # Check sign_in was called twice
        assert mock_sign_in.call_count == 2
        # First call with phone and code
        mock_sign_in.assert_any_call("123456789", "123456")
        # Second call with password only
        mock_sign_in.assert_any_call(password="2fapassword")
        assert instance._is_connected is True

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_general_error(
        self, mocker
    ):
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Get the mock instance
        mock_client_instance = mock_client_class.return_value
        # Setup and assign the dedicated AsyncMock for connect
        mock_connect = mocker.AsyncMock(side_effect=Exception("General API error"))
        mock_client_instance.connect = mock_connect
        instance._is_connected = False
        # The method should raise the exception
        with pytest.raises(Exception, match="General API error"):
            await instance._ensure_connected()
        # Assertions
        mock_connect.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Error connecting Telegram client: General API error"
        )
        assert instance._is_connected is False

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_already_connected(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance._is_connected = True
        instance.client = mocker.MagicMock()
        mock_connect = mocker.AsyncMock()
        instance.client.connect = mock_connect
        await instance._ensure_connected()
        mock_connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_auth_needed(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mocker.MagicMock()
        instance.client.connect = mocker.AsyncMock()
        instance.client.is_user_authorized = mocker.AsyncMock(return_value=False)
        instance.client.send_code_request = mocker.AsyncMock()
        instance.client.sign_in = mocker.AsyncMock()
        # Mock input to avoid hanging in tests
        mocker.patch("builtins.input", side_effect=["123456789", "12345"])
        await instance._ensure_connected()
        assert instance._is_connected is True
        instance.client.connect.assert_called_once()
        instance.client.is_user_authorized.assert_called_once()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_session_password(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mocker.MagicMock()
        instance.client.connect = mocker.AsyncMock()
        instance.client.is_user_authorized = mocker.AsyncMock(return_value=False)
        instance.client.send_code_request = mocker.AsyncMock()
        # Create a proper SessionPasswordNeededError instance
        session_error = SessionPasswordNeededError(request=mocker.MagicMock())
        instance.client.sign_in = mocker.AsyncMock(side_effect=[session_error, None])
        # Mock input to avoid hanging in tests
        mocker.patch(
            "builtins.input", side_effect=["123456789", "12345", "2fapassword"]
        )
        await instance._ensure_connected()
        assert instance._is_connected is True
        instance.client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_updaters_telegram_telegramupdater_ensure_connected_exception(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mocker.MagicMock()
        instance.client.connect = mocker.AsyncMock(
            side_effect=Exception("Connection failed")
        )
        mock_logger = mocker.patch("updaters.telegram.logger")
        with pytest.raises(Exception, match="Connection failed"):
            await instance._ensure_connected()
        assert instance._is_connected is False
        mock_logger.error.assert_called_once()

    # # _parse_message_url
    def test_updaters_telegram_telegramupdater_parse_message_url_for_no_int(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        with pytest.raises(ValueError):
            instance._parse_message_url("https://t.me/c/-a1/567")

    def test_updaters_telegram_telegramupdater_parse_message_url_for_no_message(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        with pytest.raises(ValueError):
            instance._parse_message_url("https://t.me/c/-1234")

    def test_updaters_telegram_telegramupdater_parse_message_url_functionality(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        returned = instance._parse_message_url("https://t.me/c/-1234/567")
        assert returned == (-1234, 567)

    # # _process_action
    def test_updaters_telegram_telegramupdater_process_action_success(self, mocker):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        action_callback = mocker.MagicMock()
        # Mock asyncio loop
        mock_loop = mocker.MagicMock()
        mock_loop.is_closed.return_value = False  # Add this line
        mock_new_event_loop = mocker.patch(
            "asyncio.new_event_loop", return_value=mock_loop
        )
        mock_set_event_loop = mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = instance._process_action(action_callback, "test_url", "Test reply")
        # Assertions
        assert result == mock_loop.run_until_complete.return_value
        mock_new_event_loop.assert_called_once()
        mock_set_event_loop.assert_called_once_with(mock_loop)
        mock_loop.run_until_complete.assert_called_once_with(
            action_callback("test_url", "Test reply")
        )
        # loop.close() should be called since loop.is_closed() returns False
        mock_loop.close.assert_called_once()
        mock_logger.error.assert_not_called()

    def test_updaters_telegram_telegramupdater_process_action_with_connected_client(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        instance._is_connected = True  # Client is connected

        # Create a real async function for the callback
        async def mock_action_callback(*args):
            return True

        # Mock asyncio loop
        mock_loop = mocker.MagicMock()
        # Set the return value to True
        mock_loop.run_until_complete.return_value = True
        mock_loop.is_closed.return_value = False
        mock_new_event_loop = mocker.patch(
            "asyncio.new_event_loop", return_value=mock_loop
        )
        mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = instance._process_action(
            mock_action_callback, "test_url", "Test reply"
        )
        # Assertions
        assert result is True
        mock_new_event_loop.assert_called_once()
        # Check that run_until_complete was called only once
        assert mock_loop.run_until_complete.call_count == 1
        mock_loop.close.assert_called_once()
        mock_logger.error.assert_not_called()

    def test_updaters_telegram_telegramupdater_process_action_loop_creation_error(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock asyncio to raise an exception
        mocker.patch(
            "asyncio.new_event_loop", side_effect=Exception("Loop creation failed")
        )
        action_callback = mocker.MagicMock()
        action_callback.__name__ = "creation1"
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = instance._process_action(action_callback, "test_url", "Test reply")
        # Assertions
        assert result is False
        mock_logger.error.assert_called_once_with(
            "Error raised for creation1: Loop creation failed"
        )

    def test_updaters_telegram_telegramupdater_process_action_with_existing_loop_error(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        action_callback = mocker.MagicMock()
        action_callback.__name__ = "execution1"
        # Mock asyncio with a loop that raises an exception
        mock_loop = mocker.MagicMock()
        mock_loop.run_until_complete.side_effect = Exception("Loop execution error")
        mock_loop.is_closed.return_value = False  # Add this line
        mock_loop.close = mocker.MagicMock()
        mocker.patch("asyncio.new_event_loop", return_value=mock_loop)
        mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = instance._process_action(action_callback, "test_url", "Test reply")
        # Assertions
        assert result is False
        mock_loop.run_until_complete.assert_called_once_with(
            action_callback("test_url", "Test reply")
        )
        # Should still close the loop even on error
        mock_loop.close.assert_called_once()
        mock_logger.error.assert_called_once_with(
            "Error raised for execution1: Loop execution error"
        )

    def test_updaters_telegram_telegramupdater_process_action_close_error(self, mocker):
        """Test that exception in finally block doesn't override successful result."""
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value

        # Create a real async function for the callback
        async def mock_action_callback(*args):
            return True

        # Mock asyncio loop that succeeds but has error on close
        mock_loop = mocker.MagicMock()
        # Action succeeds
        mock_loop.run_until_complete.return_value = True
        mock_loop.is_closed.return_value = False
        # Close fails
        mock_loop.close.side_effect = Exception("Close error")
        mocker.patch("asyncio.new_event_loop", return_value=mock_loop)
        mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method - should return True even though close fails
        result = instance._process_action(
            mock_action_callback, "test_url", "Test reply"
        )
        # Assertions
        # The action succeeded, so result should be True despite close error
        assert result is True
        # Loop should have been attempted to close
        mock_loop.close.assert_called_once()
        # Error during close is caught and logged as warning
        mock_logger.warning.assert_called_once_with(
            "Error closing event loop: Close error"
        )
        mock_logger.error.assert_not_called()  # No error from the action itself

    def test_updaters_telegram_telegramupdater_process_action_url_on_exception(
        self, mocker
    ):
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        # Mock asyncio
        mock_loop = mocker.MagicMock()
        mock_loop.run_until_complete.side_effect = ValueError("Invalid URL format")
        mock_loop.is_closed.return_value = False  # Add this line
        mocker.patch("asyncio.new_event_loop", return_value=mock_loop)
        mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")

        # Create action callback that will raise an exception
        async def failing_action(url, text):
            raise ValueError("Invalid URL format")

        action_callback = failing_action
        action_callback.__name__ = "name2"
        # Call the method
        result = instance._process_action(action_callback, "invalid_url", "Test reply")
        # Assertions
        assert result is False
        mock_logger.error.assert_called_once_with(
            "Error raised for name2: Invalid URL format"
        )
        # Loop should still be closed
        mock_loop.close.assert_called_once()

    def test_updaters_telegram_telegramupdater_process_action_loop_already_closed(
        self, mocker
    ):
        """Test when loop is already closed in finally block."""
        # Mock the TelegramClient
        mock_client_class = mocker.patch("updaters.telegram.TelegramClient")
        instance = TelegramUpdater()
        instance.client = mock_client_class.return_value
        action_callback = mocker.MagicMock()
        # Mock asyncio with a loop that is already closed
        mock_loop = mocker.MagicMock()
        mock_loop.is_closed.return_value = True  # Loop is already closed
        mocker.patch("asyncio.new_event_loop", return_value=mock_loop)
        mocker.patch("asyncio.set_event_loop")
        # Mock logger
        mock_logger = mocker.patch("updaters.telegram.logger")
        # Call the method
        result = instance._process_action(action_callback, "test_url", "Test reply")
        # Assertions
        assert result == mock_loop.run_until_complete.return_value
        # Should not try to close an already closed loop
        mock_loop.close.assert_not_called()
        mock_logger.error.assert_not_called()

    # # add_reaction_to_message
    def test_updaters_telegram_telegramupdater_add_reaction_to_message_functionality(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        assert (
            TelegramUpdater().add_reaction_to_message("some_url", "some_reaction")
            is True
        )

    # # add_reply_to_message
    def test_updaters_telegram_telegramupdater_add_reply_to_message_functionality(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        url, text = mocker.MagicMock(), mocker.MagicMock()
        mocked_process = mocker.patch(
            "updaters.telegram.TelegramUpdater._process_action"
        )
        updater = TelegramUpdater()
        returned = updater.add_reply_to_message(url, text)
        assert returned == mocked_process.return_value
        mocked_process.assert_called_once_with(updater._add_reply_async, url, text)

    # # message_from_url
    def test_updaters_telegram_telegramupdater_message_from_url_for_no_message_found(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        url = mocker.MagicMock()
        mocked_mention = mocker.patch(
            "updaters.telegram.Mention.objects.message_from_url", return_value=None
        )
        updater = TelegramUpdater()
        returned = updater.message_from_url(url)
        assert returned is None
        mocked_mention.assert_called_once_with(url)

    def test_updaters_telegram_telegramupdater_message_from_url_functionality(
        self, mocker
    ):
        mocker.patch("updaters.telegram.TelegramClient")
        url = mocker.MagicMock()
        message_data = mocker.MagicMock()
        mocked_mention = mocker.patch(
            "updaters.telegram.Mention.objects.message_from_url",
            return_value=message_data,
        )
        updater = TelegramUpdater()
        returned = updater.message_from_url(url)
        assert returned == message_data
        mocked_mention.assert_called_once_with(url)
