from pgai_voicebot.recordings import dual_channel_mp3_url


def test_recording_url_requests_dual_channel_mp3() -> None:
    source = "https://api.twilio.com/2010-04-01/Accounts/AC123/Recordings/RE123.json"

    assert dual_channel_mp3_url(source) == (
        "https://api.twilio.com/2010-04-01/Accounts/AC123/Recordings/RE123.mp3"
        "?RequestedChannels=2"
    )
