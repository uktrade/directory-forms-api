import pytest
import logging
from unittest.mock import patch
from gevent.server import StreamServer
from conf.gunicorn import post_fork
from gunicorn.workers.ggevent import GeventWorker
import gunicorn.util

logger = logging.getLogger(__name__)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@pytest.fixture
def worker():
    my_dict = {
        "max_requests": 1000,
        "max_requests_jitter": 10,
        "umask": 22,
        "worker_tmp_dir": "/tmp",
        "uid": 503,
        "gid": 20,
    }
    cfg_dict = dotdict(my_dict)

    worker = GeventWorker(
        log=logger,
        age=1,
        ppid=9999,
        sockets=[],
        app="directory_forms_api",
        timeout=30,
        cfg=cfg_dict,
    )
    return worker


@pytest.fixture
def server():
    def handler():
        return None

    server = StreamServer(
        listener=("0.0.0.0:8020"),
        handle=handler,
    )
    return server


@patch("conf.gunicorn.patch_with_psycogreen_gevent")
@patch.object(gunicorn.util, "chown")
def test_post_fork(mock_chown, mock_patch_with_psycogreen_gevent, worker, server):
    post_fork(server, worker)
    mock_patch_with_psycogreen_gevent.assert_called_once()
