use crate::rtos::task::{Task, TaskState};

pub struct Scheduler<const N: usize> {
    tasks: [Option<Task>; N],
    current: usize,
    pub tick: u32,
}

impl<const N: usize> Scheduler<N> {
    pub fn new() -> Self {
        Self {
            tasks: [None; N],
            current: 0,
            tick: 0,
        }
    }

    pub fn add_task(&mut self, task: Task) {
        for slot in self.tasks.iter_mut() {
            if slot.is_none() {
                *slot = Some(task);
                return;
            }
        }
        // if full: ignore for now (could log / handle error)
    }

    pub fn sleep_current(&mut self, ticks: u32) {
        if let Some(t) = &mut self.tasks[self.current] {
            // here t: &mut Task
            t.state = TaskState::Sleeping(self.tick + ticks);
        }
    }

    pub fn tick(&mut self) {
        self.tick += 1;
        for slot in self.tasks.iter_mut() {
            if let Some(t) = slot {
                // here t: &mut Task
                if let TaskState::Sleeping(wake_at) = t.state {
                    if self.tick >= wake_at {
                        t.state = TaskState::Ready;
                    }
                }
            }
        }
    }

    pub fn run_once(&mut self) {
        let len = self.tasks.len();
        for _ in 0..len {
            self.current = (self.current + 1) % len;
            if let Some(t) = &self.tasks[self.current] {
                // here t: &Task (shared ref is enough to call func)
                if let TaskState::Ready = t.state {
                    (t.func)();
                    return;
                }
            }
        }
    }
}
