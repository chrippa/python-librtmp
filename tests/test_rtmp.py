from librtmp import RTMP, RTMPError

from pytest import raises


def test_connect():
    with raises(RTMPError):
        conn = RTMP("rtmp://localhost/app/playpath", live=True)
        conn.connect()


def test_remote_method():
    conn = RTMP("rtmp://localhost/app/playpath", live=True)
    my_remote_method = conn.remote_method("MyRemoteMethod", block=True)

    assert callable(my_remote_method) == True
    assert my_remote_method.__name__ == "MyRemoteMethod"
