use std::collections::HashMap;
pub type Slk = HashMap<String, HashMap<String, String>>;

struct Pos {
    x: usize,
    y: usize
}

pub fn parse_slk(text: String) -> Slk {
    let lines = text.split('\n').map(|x| x.trim());
    let mut c = Pos { x: 0, y: 0 };
    let mut mat: HashMap<usize, HashMap<usize, String>> = HashMap::new();
    let mut end_flag = false;
    for line in lines {
        let cols: Vec<&str> = line.split(';').collect();
        match cols[0] {
            "C" => {
                for op in &cols[1..] {
                    match op.chars().next() {
                        Some('X') => c.x = op[1..].parse().unwrap(),
                        Some('Y') => c.y = op[1..].parse().unwrap(),
                        Some('K') => {
                            let mut chars: Vec<char> = op[1..].chars().collect();
                            if chars[0] == '\"' && chars[chars.len() - 1] == '\"' {
                                chars = chars[1..chars.len() - 1].to_vec();
                            }
                            mat.entry(c.y)
                                .or_insert(HashMap::new())
                                .insert(c.x, chars.into_iter().collect());
                        },
                        _ => {
                            panic!("Unknown slk operator X={} Y={}", c.x, c.y);
                        }
                    };
                }
            },
            "E" => end_flag = true,
            _ => ()
        };
    }

    if !end_flag {
        panic!("Invalid slk file {}", text);
    }
    let mut res: Slk = HashMap::new();
    // title at y=1
    let first_line = mat.remove(&1).unwrap();
    let row_keys: Vec<&String> = first_line.values().collect();
    for (_, row) in mat {
        // id at x=1
        let id = row[&1].clone();
        let target = res.entry(id).or_insert(HashMap::new());
        for (idx, val) in row {
            target.insert(row_keys[idx].to_owned(), val);
        }
    }

    res
}

#[cfg(test)]
mod tests {
    const SLK_TEXT: &'static str = r#"
        ID;P
        C;X1;Y1;K"alias"
        C;X2;K"code"
        C;X3;K"comments"
        C;X2;Y2;K"BPSE"
        C;X1;K"BPSE"
        C;Y3;K"BSTN"
        C;X2;K"BSTN"
        E
    "#;

    use super::parse_slk;

    #[test]
    fn parse_slk_test() {
        let slk = parse_slk(SLK_TEXT.to_owned());
        assert_eq!(slk.get("BPSE").unwrap().get("alias").unwrap(), "BPSE");
        assert_eq!(slk.get("BPSE").unwrap().get("code").unwrap(), "BPSE");
        assert_eq!(slk.get("BPSE").unwrap().get("comments"), None);
    }
}