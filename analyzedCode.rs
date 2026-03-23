fn main() {
    let mut data: Vec<&str> = Vec::new();
    let mut numbers: Vec<i32> = Vec::new();

    let mut attempts = 0;
    // while - уровень 1
    while attempts < 3 {
        // match с 3 ветками - уровень 2
        match attempts {
            0 => numbers.push(2),
            1 => numbers.push(-1),
            2 => data.push("rust"),
        }
        attempts += 1;
    }

    let mut sum = 0;
    let mut count = 0;

    // for - уровень 1
    for i in 0..numbers.len() {
        let n = numbers[i];
        // if/else вложенность 2
        if n > 0 {
            if n % 2 == 0 {       // уровень 3
                sum += n;         // уровень 4
            } else {
                sum += n + 1;     // уровень 4
            }
        } else {
            sum += 0;             // уровень 3
        }
    }

    // for строки - уровень 1
    for i in 0..data.len() {
        let s = data[i];
        if s.len() > 3 {           // уровень 2
            if s.len() > 4 {       // уровень 3
                count += 2;        // уровень 4
            } else {
                count += 1;        // уровень 4
            }
        } else {
            count += 1;            // уровень 2
        }
    }

    // loop - уровень 1
    let mut index = 0;
    loop {
        if index >= numbers.len() {
            break;
        }
        let n = numbers[index];
        if n % 2 == 0 {          // уровень 2
            if n > 0 {           // уровень 3
                sum += n;        // уровень 4
            } else {
                sum += 0;        // уровень 4
            }
        } else {
            if n > 0 {           // уровень 3
                sum += n + 1;    // уровень 4
            } else {
                sum += 0;        // уровень 4
            }
        }
        index += 1;
    }

    println!("sum = {}", sum);
    println!("count = {}", count);
}