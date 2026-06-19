// volume_calculator.rs - Калькулятор объёма тел на Rust (CLI)
use std::collections::HashMap;
use std::fs;
use std::io::{self, Write};
use std::str::FromStr;

const PI: f64 = std::f64::consts::PI;
const HISTORY_FILE: &str = "volume_history.json";

#[derive(serde::Serialize, serde::Deserialize, Clone)]
struct HistoryEntry {
    date: String,
    shape: String,
    params: String,
    result: String,
    units: String,
}

type ShapeFunc = fn(Vec<f64>) -> f64;

fn get_shapes() -> HashMap<String, (String, ShapeFunc, Vec<String>)> {
    let mut m = HashMap::new();
    m.insert("1".to_string(), ("Куб".to_string(), |p| p[0].powf(3.0), vec!["сторону".to_string()]));
    m.insert("2".to_string(), ("Шар".to_string(), |p| 4.0/3.0 * PI * p[0].powf(3.0), vec!["радиус".to_string()]));
    m.insert("3".to_string(), ("Цилиндр".to_string(), |p| PI * p[0].powf(2.0) * p[1], vec!["радиус".to_string(), "высоту".to_string()]));
    m.insert("4".to_string(), ("Конус".to_string(), |p| 1.0/3.0 * PI * p[0].powf(2.0) * p[1], vec!["радиус".to_string(), "высоту".to_string()]));
    m.insert("5".to_string(), ("Параллелепипед".to_string(), |p| p[0] * p[1] * p[2], vec!["длину".to_string(), "ширину".to_string(), "высоту".to_string()]));
    m.insert("6".to_string(), ("Пирамида".to_string(), |p| 1.0/3.0 * p[0] * p[1], vec!["площадь основания".to_string(), "высоту".to_string()]));
    m.insert("7".to_string(), ("Призма".to_string(), |p| p[0] * p[1], vec!["площадь основания".to_string(), "высоту".to_string()]));
    m.insert("8".to_string(), ("Тор".to_string(), |p| 2.0 * PI.powf(2.0) * p[0] * p[1].powf(2.0), vec!["большой радиус".to_string(), "малый радиус".to_string()]));
    m.insert("9".to_string(), ("Эллипсоид".to_string(), |p| 4.0/3.0 * PI * p[0] * p[1] * p[2], vec!["полуось a".to_string(), "полуось b".to_string(), "полуось c".to_string()]));
    m.insert("10".to_string(), ("Усечённый конус".to_string(), |p| 1.0/3.0 * PI * p[2] * (p[0].powf(2.0) + p[0]*p[1] + p[1].powf(2.0)), vec!["радиус 1".to_string(), "радиус 2".to_string(), "высоту".to_string()]));
    m
}

fn save_history(entry: &HistoryEntry) {
    let mut history: Vec<HistoryEntry> = Vec::new();
    if let Ok(data) = fs::read_to_string(HISTORY_FILE) {
        if let Ok(parsed) = serde_json::from_str(&data) {
            history = parsed;
        }
    }
    history.push(entry.clone());
    let json = serde_json::to_string_pretty(&history).unwrap();
    fs::write(HISTORY_FILE, json).unwrap();
}

fn load_history() -> Vec<HistoryEntry> {
    if let Ok(data) = fs::read_to_string(HISTORY_FILE) {
        if let Ok(parsed) = serde_json::from_str(&data) {
            return parsed;
        }
    }
    Vec::new()
}

fn export_csv(filename: &str) {
    let history = load_history();
    if history.is_empty() {
        println!("История пуста.");
        return;
    }
    let mut content = String::from("Дата,Фигура,Параметры,Объём,Единицы\n");
    for e in &history {
        let units = if e.units.is_empty() { "куб. ед." } else { &e.units };
        content.push_str(&format!("{},{},{},{},{}\n", &e.date[..19], e.shape, e.params, e.result, units));
    }
    fs::write(filename, content).unwrap();
    println!("Экспортировано в {}", filename);
}

fn read_line(prompt: &str) -> String {
    print!("{}", prompt);
    io::stdout().flush().unwrap();
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    input.trim().to_string()
}

fn get_float(prompt: &str) -> f64 {
    loop {
        let input = read_line(prompt);
        if let Ok(val) = f64::from_str(&input) {
            if val > 0.0 {
                return val;
            }
        }
        println!("Введите положительное число.");
    }
}

fn main() {
    println!("📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ");
    let shapes = get_shapes();
    let mut history = load_history();
    let mut units = "куб. ед.".to_string();

    loop {
        println!("\nВыберите фигуру:");
        for (key, (name, _, _)) in &shapes {
            println!("{}. {}", key, name);
        }
        println!("h. Показать историю");
        println!("e. Экспорт CSV");
        println!("u. Сменить единицы");
        println!("0. Выход");

        let choice = read_line("Ваш выбор: ");

        if choice == "0" {
            break;
        } else if choice == "h" {
            if history.is_empty() {
                println!("История пуста.");
            } else {
                println!("\n=== ИСТОРИЯ ===");
                let start = if history.len() > 10 { history.len() - 10 } else { 0 };
                for entry in &history[start..] {
                    println!("{} | {} | {}", &entry.date[..19], entry.shape, entry.result);
                }
            }
            continue;
        } else if choice == "e" {
            let filename = read_line("Имя CSV файла (по умолчанию volume_history.csv): ");
            let filename = if filename.is_empty() { "volume_history.csv" } else { &filename };
            export_csv(filename);
            continue;
        } else if choice == "u" {
            println!("Доступные единицы: куб. ед., см³, м³, дм³, л, in³");
            let input = read_line("Выберите единицы: ");
            if !input.is_empty() {
                units = input;
            }
            continue;
        } else if let Some((name, func, param_names)) = shapes.get(&choice) {
            println!("\nФигура: {}", name);
            let mut params = Vec::new();
            for pname in param_names {
                params.push(get_float(&format!("Введите {}: ", pname)));
            }
            let result = func(params.clone());
            let result_str = format!("{:.4} {}", result, units);
            println!("\nОбъём {}: {}", name.to_lowercase(), result_str);

            let save = read_line("Сохранить результат? (y/n): ");
            if save.to_lowercase() == "y" {
                let entry = HistoryEntry {
                    date: chrono::Local::now().to_rfc3339(),
                    shape: name.clone(),
                    params: params.iter().map(|p| p.to_string()).collect::<Vec<_>>().join(", "),
                    result: result_str.clone(),
                    units: units.clone(),
                };
                save_history(&entry);
                history.push(entry);
                println!("✅ Сохранено!");
            }
        } else {
            println!("Неверный выбор.");
        }
    }
}
