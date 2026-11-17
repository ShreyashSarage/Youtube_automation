# Rust Zero to Pro: 90-day Shorts plan

One beginner-friendly Rust lesson every day, uploaded around 11:00 IST and public at **12:00 IST**.
Days 1–2 are posted; the daily automation takes the next unposted day from `state/curriculum.json` (this file is generated from it).
Sources are The Rust Book and Rust by Example; every code example is compiled before posting.


## Already posted  (Days 1–2)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 1 ✅ | Mon 16 Nov | [What is Rust & why learn it](https://doc.rust-lang.org/book/ch00-00-introduction.html) | fast like C/C++, memory safe without a GC, great tooling (cargo), used by big companies |
| 2 ✅ | Tue 17 Nov | [Install Rust & Hello, World!](https://doc.rust-lang.org/book/ch01-01-installation.html) | rustup installs rustc+cargo; fn main; println! macro; rustc main.rs |

## Week 1: Getting started  (Days 3–9)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 3 | Wed 18 Nov | [Cargo: your Rust toolbox](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html) | cargo new, cargo build, cargo run, cargo check, Cargo.toml and target/ |
| 4 | Thu 19 Nov | [Variables & mutability](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html) | let is immutable by default; let mut; the 'cannot assign twice' error E0384 |
| 5 | Fri 20 Nov | [Constants & shadowing](https://doc.rust-lang.org/book/ch03-01-variables-and-mutability.html) | const needs a type; shadowing with let x = x + 1 makes a new variable, can change type |
| 6 | Sat 21 Nov | [Integers & floats](https://doc.rust-lang.org/book/ch03-02-data-types.html) | i32 is the default integer, u8..u128 / i8..i128, f64 default float, number literals 1_000 |
| 7 | Sun 22 Nov | [bool, char & integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html) | bool; char is 4-byte Unicode; overflow panics in debug, wraps in release; checked_add / wrapping_add |
| 8 | Mon 23 Nov | [Tuples & arrays](https://doc.rust-lang.org/book/ch03-02-data-types.html) | tuples (i32, f64) with .0 and destructuring; arrays [i32; 5]; out-of-bounds index panics |
| 9 | Tue 24 Nov | [Functions](https://doc.rust-lang.org/book/ch03-03-how-functions-work.html) | fn name(x: i32) -> i32; parameters need types; snake_case |

## Week 2: Control flow & printing  (Days 10–16)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 10 | Wed 25 Nov | [Statements vs expressions](https://doc.rust-lang.org/book/ch03-03-how-functions-work.html) | blocks are expressions; the last expression without ; is the value; why adding ; breaks a return |
| 11 | Thu 26 Nov | [if / else](https://doc.rust-lang.org/book/ch03-05-control-flow.html) | conditions must be bool; if is an expression: let x = if c { 1 } else { 2 }; |
| 12 | Fri 27 Nov | [loop & break with a value](https://doc.rust-lang.org/book/ch03-05-control-flow.html) | loop { }; break value; returning a value from loop; continue |
| 13 | Sat 28 Nov | [while, for & ranges](https://doc.rust-lang.org/book/ch03-05-control-flow.html) | while; for x in collection; 0..5 vs 0..=5; .rev() |
| 14 | Sun 29 Nov | [Loop labels](https://doc.rust-lang.org/book/ch03-05-control-flow.html) | 'outer: loop { break 'outer; } to break out of nested loops |
| 15 | Mon 30 Nov | [Comments & doc comments](https://doc.rust-lang.org/book/ch03-04-comments.html) | // comments, /// doc comments, cargo doc --open |
| 16 | Tue 01 Dec | [println! formatting](https://doc.rust-lang.org/rust-by-example/hello/print.html) | {} vs {:?}, inline {x}, width/alignment {:>5}, precision {:.2}, eprintln! |

## Week 3: Ownership  (Days 17–23)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 17 | Wed 02 Dec | [Ownership: the 3 rules](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) | one owner per value; one owner at a time; value dropped when owner goes out of scope |
| 18 | Thu 03 Dec | [Stack vs heap](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) | fixed-size data on the stack; String's buffer on the heap; pointer, length, capacity |
| 19 | Fri 04 Dec | [Move semantics](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) | let s2 = s1 moves a String; using s1 after is error E0382 |
| 20 | Sat 05 Dec | [Copy vs Clone](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) | integers/bool/char are Copy; .clone() makes a deep copy of a String |
| 21 | Sun 06 Dec | [Ownership & functions](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) | passing a String to a function moves it; returning gives ownership back |
| 22 | Mon 07 Dec | [References & borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) | &s borrows without taking ownership; the owner stays valid |
| 23 | Tue 08 Dec | [Mutable references](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) | &mut s; only one mutable reference at a time (E0499); no mixing & and &mut |

## Week 4: Slices, strings & structs  (Days 24–30)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 24 | Wed 09 Dec | [No dangling references](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) | the compiler rejects returning a reference to a local (E0106); return the owned value instead |
| 25 | Thu 10 Dec | [Slices](https://doc.rust-lang.org/book/ch04-03-slices.html) | &s[0..5], &str is a string slice, array slices &a[1..3] |
| 26 | Fri 11 Dec | [String vs &str](https://doc.rust-lang.org/book/ch08-02-strings.html) | String is owned and growable, &str is borrowed; String::from, .to_string(), &s as &str |
| 27 | Sat 12 Dec | [Working with Strings](https://doc.rust-lang.org/book/ch08-02-strings.html) | push_str, push, + and format!, why s[0] doesn't compile, .chars() and .bytes() |
| 28 | Sun 13 Dec | [Structs](https://doc.rust-lang.org/book/ch05-01-defining-structs.html) | struct User { name: String, age: u32 }, field init shorthand, struct update syntax .. |
| 29 | Mon 14 Dec | [Tuple structs & unit structs](https://doc.rust-lang.org/book/ch05-01-defining-structs.html) | struct Point(i32, i32); struct Marker; newtype idea |
| 30 | Tue 15 Dec | [Methods with impl](https://doc.rust-lang.org/book/ch05-03-method-syntax.html) | impl Rect { fn area(&self) -> u32 }, &self vs &mut self vs self |

## Week 5: Enums & pattern matching  (Days 31–37)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 31 | Wed 16 Dec | [Associated functions & new()](https://doc.rust-lang.org/book/ch05-03-method-syntax.html) | fn new(...) -> Self called as Type::new; multiple impl blocks |
| 32 | Thu 17 Dec | [#[derive(Debug)] & dbg!](https://doc.rust-lang.org/book/ch05-02-example-structs.html) | printing structs with {:?} and {:#?}; dbg! prints file, line and value |
| 33 | Fri 18 Dec | [Enums](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) | enum Direction { Up, Down }; variants with data: enum Message { Move { x: i32, y: i32 }, Write(String) } |
| 34 | Sat 19 Dec | [Option: no more null](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) | Option<T> is Some(T) or None; you must handle None |
| 35 | Sun 20 Dec | [match](https://doc.rust-lang.org/book/ch06-02-match.html) | match must be exhaustive (E0004); arms bind values; _ catch-all |
| 36 | Mon 21 Dec | [if let & let else](https://doc.rust-lang.org/book/ch06-03-if-let.html) | if let Some(x) = opt { }; let Some(x) = opt else { return; }; |
| 37 | Tue 22 Dec | [Pattern matching power moves](https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html) | ranges 1..=5, | alternatives, match guards if x > 5, @ bindings, destructuring |

## Week 6: Organising code & collections  (Days 38–44)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 38 | Wed 23 Dec | [Modules & pub](https://doc.rust-lang.org/book/ch07-02-defining-modules-to-control-scope-and-privacy.html) | mod, privacy by default, pub fn, pub struct fields |
| 39 | Thu 24 Dec | [use & paths](https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html) | crate::, self::, super::, use to shorten paths, use ... as |
| 40 | Fri 25 Dec | [Modules in files](https://doc.rust-lang.org/book/ch07-05-separating-modules-into-different-files.html) | mod foo; looks for foo.rs or foo/mod.rs; splitting a project |
| 41 | Sat 26 Dec | [Vec<T>](https://doc.rust-lang.org/book/ch08-01-vectors.html) | Vec::new, vec![1, 2, 3], push, get returns Option, indexing can panic |
| 42 | Sun 27 Dec | [Iterating & changing a Vec](https://doc.rust-lang.org/book/ch08-01-vectors.html) | for x in &v, for x in &mut v with *x += 1, why you can't push while borrowing |
| 43 | Mon 28 Dec | [HashMap](https://doc.rust-lang.org/book/ch08-03-hash-maps.html) | use std::collections::HashMap; insert, get, iterate |
| 44 | Tue 29 Dec | [HashMap entry API](https://doc.rust-lang.org/book/ch08-03-hash-maps.html) | entry(k).or_insert(0) and += 1 to count words |

## Week 7: Error handling  (Days 45–51)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 45 | Wed 30 Dec | [panic!](https://doc.rust-lang.org/book/ch09-01-unrecoverable-errors-with-panic.html) | unrecoverable errors; RUST_BACKTRACE=1; panics on out-of-bounds |
| 46 | Thu 31 Dec | [Result<T, E>](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) | Ok and Err; matching on File::open; handling different error kinds |
| 47 | Fri 01 Jan | [The ? operator](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) | propagates errors early; works in functions returning Result or Option |
| 48 | Sat 02 Jan | [unwrap & expect](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html) | unwrap panics on Err/None; expect adds a message; when it's fine to use them |
| 49 | Sun 03 Jan | [main can return Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) | fn main() -> Result<(), Box<dyn Error>> to use ? in main |
| 50 | Mon 04 Jan | [Option combinators](https://doc.rust-lang.org/rust-by-example/error/option_unwrap/map.html) | map, and_then, unwrap_or, unwrap_or_default, ok_or |
| 51 | Tue 05 Jan | [Custom error types](https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/define_error_type.html) | an error enum, impl Display, impl From<io::Error> so ? converts automatically |

## Week 8: Generics & traits  (Days 52–58)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 52 | Wed 06 Jan | [Generic functions](https://doc.rust-lang.org/book/ch10-01-syntax.html) | fn largest<T: PartialOrd>(list: &[T]) -> &T; zero-cost via monomorphization |
| 53 | Thu 07 Jan | [Generic structs & enums](https://doc.rust-lang.org/book/ch10-01-syntax.html) | struct Point<T> { x: T, y: T }; Option<T> and Result<T, E> are generic enums |
| 54 | Fri 08 Jan | [Traits](https://doc.rust-lang.org/book/ch10-02-traits.html) | trait Summary { fn summarize(&self) -> String; } implemented for different types |
| 55 | Sat 09 Jan | [Default trait methods](https://doc.rust-lang.org/book/ch10-02-traits.html) | a default body in the trait; overriding it |
| 56 | Sun 10 Jan | [Trait bounds & where](https://doc.rust-lang.org/book/ch10-02-traits.html) | fn notify<T: Summary>(item: &T); multiple bounds with +; where clauses |
| 57 | Mon 11 Jan | [impl Trait](https://doc.rust-lang.org/book/ch10-02-traits.html) | fn f(x: &impl Summary) and returning impl Trait |
| 58 | Tue 12 Jan | [Derive traits](https://doc.rust-lang.org/book/appendix-03-derivable-traits.html) | #[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord, Default)] |

## Week 9: Traits in practice & lifetimes  (Days 59–65)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 59 | Wed 13 Jan | [Display trait](https://doc.rust-lang.org/rust-by-example/hello/print/print_display.html) | impl fmt::Display for your type so {} works |
| 60 | Thu 14 Jan | [Operator overloading](https://doc.rust-lang.org/book/ch20-02-advanced-traits.html) | impl Add for Point so p1 + p2 works |
| 61 | Fri 15 Jan | [From & Into](https://doc.rust-lang.org/rust-by-example/conversion/from_into.html) | impl From<i32> for Number; .into() comes for free |
| 62 | Sat 16 Jan | [Lifetimes explained](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) | 'a ties reference lifetimes: fn longest<'a>(x: &'a str, y: &'a str) -> &'a str |
| 63 | Sun 17 Jan | [Lifetime elision](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) | the three elision rules: why most functions need no 'a |
| 64 | Mon 18 Jan | [Lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) | struct Excerpt<'a> { part: &'a str } can't outlive what it borrows |
| 65 | Tue 19 Jan | ['static](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) | string literals are &'static str; what 'static really means |

## Week 10: Closures & iterators  (Days 66–72)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 66 | Wed 20 Jan | [Closures](https://doc.rust-lang.org/book/ch13-01-closures.html) | |x| x + 1; type inference; capturing the environment |
| 67 | Thu 21 Jan | [Fn, FnMut, FnOnce & move](https://doc.rust-lang.org/book/ch13-01-closures.html) | how closures capture; move closures take ownership |
| 68 | Fri 22 Jan | [Iterators](https://doc.rust-lang.org/book/ch13-02-iterators.html) | iter(), into_iter(), iter_mut(); iterators are lazy until consumed |
| 69 | Sat 23 Jan | [map, filter, collect](https://doc.rust-lang.org/book/ch13-02-iterators.html) | chaining adapters; collect::<Vec<_>>() |
| 70 | Sun 24 Jan | [Iterator power moves](https://doc.rust-lang.org/rust-by-example/trait/iter.html) | enumerate, zip, take, skip, sum, fold, any, all |
| 71 | Mon 25 Jan | [Implementing Iterator](https://doc.rust-lang.org/book/ch13-02-iterators.html) | impl Iterator for Counter { type Item; fn next(&mut self) -> Option<Self::Item> } |
| 72 | Tue 26 Jan | [Loops vs iterators performance](https://doc.rust-lang.org/book/ch13-04-performance.html) | iterators compile to the same machine code: zero-cost abstractions |

## Week 11: Smart pointers  (Days 73–79)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 73 | Wed 27 Jan | [Box<T>](https://doc.rust-lang.org/book/ch15-01-box.html) | heap allocation; recursive types: enum List { Cons(i32, Box<List>), Nil } |
| 74 | Thu 28 Jan | [Deref & deref coercion](https://doc.rust-lang.org/book/ch15-02-deref.html) | * on Box; impl Deref; &String becomes &str automatically |
| 75 | Fri 29 Jan | [Drop](https://doc.rust-lang.org/book/ch15-03-drop.html) | drop runs when a value goes out of scope (RAII); std::mem::drop |
| 76 | Sat 30 Jan | [Rc<T>](https://doc.rust-lang.org/book/ch15-04-rc.html) | shared ownership; Rc::clone; Rc::strong_count; single-threaded only |
| 77 | Sun 31 Jan | [RefCell<T>](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html) | interior mutability; borrow and borrow_mut checked at runtime; panics on violation |
| 78 | Mon 01 Feb | [Rc<RefCell<T>>](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html) | multiple owners of mutable data |
| 79 | Tue 02 Feb | [Weak & reference cycles](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html) | cycles leak with Rc; Weak<T> and upgrade() |

## Week 12: Concurrency  (Days 80–86)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 80 | Wed 03 Feb | [Threads](https://doc.rust-lang.org/book/ch16-01-threads.html) | std::thread::spawn and JoinHandle::join |
| 81 | Thu 04 Feb | [move closures with threads](https://doc.rust-lang.org/book/ch16-01-threads.html) | why threads need move; borrowing across threads is rejected |
| 82 | Fri 05 Feb | [Channels](https://doc.rust-lang.org/book/ch16-02-message-passing.html) | mpsc::channel, tx.send, rx.recv, multiple producers with tx.clone() |
| 83 | Sat 06 Feb | [Mutex](https://doc.rust-lang.org/book/ch16-03-shared-state.html) | Mutex::new, lock(), the guard unlocks on drop |
| 84 | Sun 07 Feb | [Arc<Mutex<T>>](https://doc.rust-lang.org/book/ch16-03-shared-state.html) | sharing a counter across threads; why Rc doesn't work there |
| 85 | Mon 08 Feb | [Send & Sync](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html) | marker traits; the compiler prevents data races at compile time |
| 86 | Tue 09 Feb | [Async/await basics](https://doc.rust-lang.org/book/ch17-01-futures-and-syntax.html) | async fn returns a future; .await; futures are lazy |

## Week 13: Real-world Rust  (Days 87–90)

| Day | Date | Lesson | What it covers |
|---|---|---|---|
| 87 | Wed 10 Feb | [Trait objects: dyn Trait](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) | Vec<Box<dyn Draw>>; dynamic vs static dispatch |
| 88 | Thu 11 Feb | [Writing tests](https://doc.rust-lang.org/book/ch11-01-writing-tests.html) | #[test], assert_eq!, cargo test, #[cfg(test)] mod tests |
| 89 | Fri 12 Feb | [Declarative macros](https://doc.rust-lang.org/book/ch20-05-macros.html) | macro_rules!, how vec! works, repetition $( ),* |
| 90 | Sat 13 Feb | [Capstone: what to build next](https://doc.rust-lang.org/book/ch21-00-final-project-a-web-server.html) | recap of the 90 days; project ideas: CLI tool (Book ch12), web server (ch21), contribute to open source |

## Notes
- Odd days use the cyan *ocean* look, even days the green *matrix* look (the two reference styles).
- Each Short: hook → concept animation → real code → what happens → common mistake → recap → "Tomorrow:" teaser.
- To change the plan, edit `state/curriculum.json` (keep `day` numbers in order); the next daily run picks it up.
