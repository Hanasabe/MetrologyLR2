fn main() {
    let mut data: Vec<&str> = Vec::new();
    let mut numbers: Vec<i32> = Vec::new();

    let mut attempts = 0;
    while attempts < 3 {
        match attempts {
            0 => numbers.push(2),
            1 => numbers.push(-1),
            2 => data.push("rust"),
        }
        attempts += 1;
    }

    let mut sum = 0;
    let mut count = 0;

    for i in 0..numbers.len() {
        let n = numbers[i];
        if n > 0 {
            if n % 2 == 0 {
                if sum < n {
                    for i in 0..n {
                        if sum != n {
                            sum += n;
                        }
                    }
                }
            } else {
                sum += n + 1;
            }
        } else {
            for i in 0..(-n) {
                match sum {
                    1 => sum += 1,
                    -1 => sum += 2,
                    0 => sum += 3,
                }
            }
        }
    }

    for i in 0..data.len() {
        let s = data[i];
        if s.len() > 3 {
            if s.len() > 4 {
                count += 2;
            } else {
                count += 1;
            }
        } else {
            count += 1;
        }
    }

    let mut index = 0;
    loop {
        if index >= numbers.len() {
            break;
        }
        let n = numbers[index];
        if n % 2 == 0 {
            if n > 0 {
                sum += n;
            } else {
                sum += 0;
            }
        } else {
            if n > 0 {
                sum += n + 1;
            } else {
                sum += 0;
            }
        }
        index += 1;
    }

    println!("sum = {}", sum);
    println!("count = {}", count);
}
