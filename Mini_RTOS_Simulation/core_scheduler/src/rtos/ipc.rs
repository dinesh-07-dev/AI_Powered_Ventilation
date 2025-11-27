pub struct MsgQueue<T, const N: usize> {
    buffer: [Option<T>; N],
    head: usize,
    tail: usize,
}

impl<T: Copy, const N: usize> MsgQueue<T, N> {
    pub fn new() -> Self {
        Self {
            buffer: [None; N],
            head: 0,
            tail: 0,
        }
    }

    pub fn send(&mut self, msg: T) -> bool {
        let next_head = (self.head + 1) % N;
        if next_head == self.tail {
            return false; // full
        }
        self.buffer[self.head] = Some(msg);
        self.head = next_head;
        true
    }

    pub fn recv(&mut self) -> Option<T> {
        if self.tail == self.head {
            return None; // empty
        }
        let msg = self.buffer[self.tail];
        self.buffer[self.tail] = None;
        self.tail = (self.tail + 1) % N;
        msg
    }
}
