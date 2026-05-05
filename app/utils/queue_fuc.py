import queue
class Queue_All:
    def __init__(self):
        self.queues: dict[str, queue.Queue] = {}

    # =========================
    # Tạo queue (generic)
    # =========================
    def create_queue(self, name: str, maxsize: int = 0):
        """
        Tạo một queue mới theo tên.

        name    : tên queue
        maxsize : kích thước queue (0 = không giới hạn)
        """
        if name not in self.queues:
            self.queues[name] = queue.Queue(maxsize=maxsize)
        return self.queues[name]

    # =========================
    # Put dữ liệu (generic)
    # =========================
    def put(self, name: str, data) -> bool:
        """
        Đưa dữ liệu vào queue theo tên.
        """
        q = self.queues.get(name)
        if not q:
            return False

        try:
            q.put_nowait(data)
            return True
        except queue.Full:
            return False

    # =========================
    # Get dữ liệu (generic)
    # =========================
    def get(self, name: str):
        """
        Lấy dữ liệu từ queue theo tên.
        """
        q = self.queues.get(name)
        if not q:
            return None
        try:
            return q.get_nowait()
        except queue.Empty:
            return None
    def clear(self, name: str):
        """Xóa toàn bộ dữ liệu trong queue theo tên"""
        q = self.queues.get(name)
        if not q:
            return

        with q.mutex:
            q.queue.clear()

    def get_timeout(self, name: str, timeout=None):
        q = self.queues.get(name)
        if not q:
            return None
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None
