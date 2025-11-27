mod rtos;

use rtos::task::Task;
use rtos::scheduler::Scheduler;
use rtos::ipc::MsgQueue;

static mut QUEUE: Option<MsgQueue<u32, 8>> = None;

fn task_producer() {
    unsafe {
        if let Some(ref mut q) = QUEUE {
            let _ = q.send(42);
        }
    }
    println!("[producer] sent 42");
}

fn task_consumer() {
    unsafe {
        if let Some(ref mut q) = QUEUE {
            if let Some(v) = q.recv() {
                println!("[consumer] received {}", v);
            } else {
                println!("[consumer] queue empty");
            }
        }
    }
}

fn main() {
    // init global queue
    unsafe {
        QUEUE = Some(MsgQueue::new());
    }

    let mut sched: Scheduler<4> = Scheduler::new();
    sched.add_task(Task::new(0, task_producer));
    sched.add_task(Task::new(1, task_consumer));

    // simulate ticks
    for _ in 0..10 {
        sched.tick();
        sched.run_once();
    }
}