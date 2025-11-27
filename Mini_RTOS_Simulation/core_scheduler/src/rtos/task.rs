#[derive(Copy, Clone, Debug)]
pub enum TaskState {
    Ready,
    Blocked,
    Sleeping(u32), // wake at tick
}

pub type TaskFn = fn();

#[derive(Copy, Clone)]
pub struct Task {
    pub id: u8,
    pub func: TaskFn,
    pub state: TaskState,
}

impl Task {
    pub const fn new(id: u8, func: TaskFn) -> Self {
        Self {
            id,
            func,
            state: TaskState::Ready,
        }
    }
}
