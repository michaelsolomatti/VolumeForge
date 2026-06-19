<?php
// volume_calculator.php - Калькулятор объёма тел на PHP (CLI + веб)
// CLI: php volume_calculator.php

const PI = M_PI;
const HISTORY_FILE = 'volume_history.json';

$shapes = [
    '1' => ['name' => 'Куб', 'func' => function($p) { return pow($p[0], 3); }, 'params' => ['сторону']],
    '2' => ['name' => 'Шар', 'func' => function($p) { return 4/3 * PI * pow($p[0], 3); }, 'params' => ['радиус']],
    '3' => ['name' => 'Цилиндр', 'func' => function($p) { return PI * pow($p[0], 2) * $p[1]; }, 'params' => ['радиус', 'высоту']],
    '4' => ['name' => 'Конус', 'func' => function($p) { return 1/3 * PI * pow($p[0], 2) * $p[1]; }, 'params' => ['радиус', 'высоту']],
    '5' => ['name' => 'Параллелепипед', 'func' => function($p) { return $p[0] * $p[1] * $p[2]; }, 'params' => ['длину', 'ширину', 'высоту']],
    '6' => ['name' => 'Пирамида', 'func' => function($p) { return 1/3 * $p[0] * $p[1]; }, 'params' => ['площадь основания', 'высоту']],
    '7' => ['name' => 'Призма', 'func' => function($p) { return $p[0] * $p[1]; }, 'params' => ['площадь основания', 'высоту']],
    '8' => ['name' => 'Тор', 'func' => function($p) { return 2 * pow(PI, 2) * $p[0] * pow($p[1], 2); }, 'params' => ['большой радиус', 'малый радиус']],
    '9' => ['name' => 'Эллипсоид', 'func' => function($p) { return 4/3 * PI * $p[0] * $p[1] * $p[2]; }, 'params' => ['полуось a', 'полуось b', 'полуось c']],
    '10' => ['name' => 'Усечённый конус', 'func' => function($p) { return 1/3 * PI * $p[2] * (pow($p[0], 2) + $p[0]*$p[1] + pow($p[1], 2)); }, 'params' => ['радиус 1', 'радиус 2', 'высоту']],
];

function saveHistory($entry) {
    $history = [];
    if (file_exists(HISTORY_FILE)) {
        $json = file_get_contents(HISTORY_FILE);
        $history = json_decode($json, true) ?: [];
    }
    $history[] = $entry;
    file_put_contents(HISTORY_FILE, json_encode($history, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function loadHistory() {
    if (file_exists(HISTORY_FILE)) {
        $json = file_get_contents(HISTORY_FILE);
        return json_decode($json, true) ?: [];
    }
    return [];
}

function exportCSV($filename) {
    $history = loadHistory();
    if (empty($history)) {
        echo "История пуста.\n";
        return;
    }
    $f = fopen($filename, 'w');
    fputcsv($f, ['Дата', 'Фигура', 'Параметры', 'Объём', 'Единицы']);
    foreach ($history as $entry) {
        $units = $entry['units'] ?? 'куб. ед.';
        fputcsv($f, [substr($entry['date'], 0, 19), $entry['shape'], $entry['params'], $entry['result'], $units]);
    }
    fclose($f);
    echo "Экспортировано в $filename\n";
}

function getFloat($prompt) {
    while (true) {
        echo $prompt;
        $input = trim(fgets(STDIN));
        if (is_numeric($input) && $input > 0) {
            return (float)$input;
        }
        echo "Введите положительное число.\n";
    }
}

if (php_sapi_name() === 'cli') {
    // CLI режим
    echo "📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ\n";
    $history = loadHistory();
    $units = 'куб. ед.';
    global $shapes;

    while (true) {
        echo "\nВыберите фигуру:\n";
        foreach ($shapes as $key => $shape) {
            echo "$key. " . $shape['name'] . "\n";
        }
        echo "h. Показать историю\n";
        echo "e. Экспорт CSV\n";
        echo "u. Сменить единицы\n";
        echo "0. Выход\n";
        echo "Ваш выбор: ";
        $choice = trim(fgets(STDIN));

        if ($choice == '0') break;
        elseif ($choice == 'h') {
            if (empty($history)) {
                echo "История пуста.\n";
            } else {
                echo "\n=== ИСТОРИЯ ===\n";
                $recent = array_slice($history, -10);
                foreach ($recent as $entry) {
                    echo substr($entry['date'], 0, 19) . " | " . $entry['shape'] . " | " . $entry['result'] . "\n";
                }
            }
            continue;
        } elseif ($choice == 'e') {
            echo "Имя CSV файла (по умолчанию volume_history.csv): ";
            $filename = trim(fgets(STDIN));
            if (empty($filename)) $filename = 'volume_history.csv';
            exportCSV($filename);
            continue;
        } elseif ($choice == 'u') {
            echo "Доступные единицы: куб. ед., см³, м³, дм³, л, in³\n";
            echo "Выберите единицы: ";
            $input = trim(fgets(STDIN));
            if (!empty($input)) $units = $input;
            continue;
        } elseif (isset($shapes[$choice])) {
            $shape = $shapes[$choice];
            echo "\nФигура: " . $shape['name'] . "\n";
            $params = [];
            foreach ($shape['params'] as $pname) {
                $params[] = getFloat("Введите $pname: ");
            }
            $result = $shape['func']($params);
            $resultStr = number_format($result, 4) . " " . $units;
            echo "\nОбъём " . strtolower($shape['name']) . ": $resultStr\n";

            echo "Сохранить результат? (y/n): ";
            $save = trim(fgets(STDIN));
            if (strtolower($save) == 'y') {
                $entry = [
                    'date' => date('c'),
                    'shape' => $shape['name'],
                    'params' => implode(', ', $params),
                    'result' => $resultStr,
                    'units' => $units
                ];
                saveHistory($entry);
                $history[] = $entry;
                echo "✅ Сохранено!\n";
            }
        } else {
            echo "Неверный выбор.\n";
        }
    }
    exit;
}

// ========== ВЕБ-ИНТЕРФЕЙС ==========
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📦 Калькулятор объёма тел (PHP)</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7fb; margin: 20px; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 20px; border-radius: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 140px; }
        input, select, button { padding: 6px; border-radius: 4px; border: 1px solid #ccc; }
        button { background: #3498db; color: white; border: none; cursor: pointer; padding: 6px 20px; }
        button:hover { background: #2980b9; }
        .result { background: #ecf0f1; padding: 15px; border-radius: 8px; margin-top: 20px; }
        .history { margin-top: 20px; background: #f8f9fa; padding: 10px; border-radius: 8px; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
<div class="container">
    <h1>📦 Калькулятор объёма тел (PHP)</h1>
    <form method="GET">
        <div class="form-group">
            <label>Выберите фигуру:</label>
            <select name="shape">
                <?php foreach ($shapes as $key => $shape): ?>
                    <option value="<?= $key ?>" <?= isset($_GET['shape']) && $_GET['shape'] == $key ? 'selected' : '' ?>>
                        <?= $shape['name'] ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>
        <div id="params-container">
            <?php if (isset($_GET['shape']) && isset($shapes[$_GET['shape']])): 
                $selected = $shapes[$_GET['shape']];
                foreach ($selected['params'] as $idx => $pname): ?>
                    <div class="form-group">
                        <label>Введите <?= $pname ?>:</label>
                        <input type="number" step="any" name="param_<?= $idx ?>" value="<?= $_GET["param_$idx"] ?? '' ?>" required>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
        <div class="form-group">
            <label>Единицы измерения:</label>
            <select name="units">
                <option value="куб. ед." <?= isset($_GET['units']) && $_GET['units'] == 'куб. ед.' ? 'selected' : '' ?>>куб. ед.</option>
                <option value="см³" <?= isset($_GET['units']) && $_GET['units'] == 'см³' ? 'selected' : '' ?>>см³</option>
                <option value="м³" <?= isset($_GET['units']) && $_GET['units'] == 'м³' ? 'selected' : '' ?>>м³</option>
                <option value="дм³" <?= isset($_GET['units']) && $_GET['units'] == 'дм³' ? 'selected' : '' ?>>дм³</option>
                <option value="л" <?= isset($_GET['units']) && $_GET['units'] == 'л' ? 'selected' : '' ?>>литры</option>
                <option value="in³" <?= isset($_GET['units']) && $_GET['units'] == 'in³' ? 'selected' : '' ?>>in³</option>
            </select>
        </div>
        <button type="submit">Рассчитать</button>
        <a href="?export=1">📥 Экспорт CSV</a>
    </form>

    <?php if (isset($_GET['shape']) && isset($_GET['param_0'])): 
        $shape = $shapes[$_GET['shape']];
        $params = [];
        for ($i = 0; $i < count($shape['params']); $i++) {
            if (!isset($_GET["param_$i"]) || $_GET["param_$i"] === '') break;
            $val = (float)$_GET["param_$i"];
            if ($val <= 0) { echo "<div class='result' style='background:#fadbd8;'>Ошибка: все параметры должны быть положительными.</div>"; break 2; }
            $params[] = $val;
        }
        if (count($params) == count($shape['params'])) {
            $units = $_GET['units'] ?? 'куб. ед.';
            $result = $shape['func']($params);
            $resultStr = number_format($result, 4) . " " . $units;
            echo "<div class='result'><strong>Результат:</strong> Объём " . strtolower($shape['name']) . " = $resultStr</div>";
            // Сохранение в историю
            $entry = [
                'date' => date('c'),
                'shape' => $shape['name'],
                'params' => implode(', ', $params),
                'result' => $resultStr,
                'units' => $units
            ];
            saveHistory($entry);
        }
    endif; ?>

    <?php if (isset($_GET['export'])): 
        exportCSV('volume_history.csv');
        echo "<div class='result'>✅ История сохранена в volume_history.csv</div>";
    endif; ?>

    <div class="history">
        <h3>📊 Последние вычисления</h3>
        <?php $history = loadHistory(); ?>
        <?php if (empty($history)): ?>
            <p>История пуста.</p>
        <?php else: ?>
            <?php foreach (array_slice($history, -5) as $entry): ?>
                <div style="border-bottom:1px solid #eee; padding:5px 0;">
                    <strong><?= $entry['shape'] ?></strong> = <?= $entry['result'] ?>
                    <span style="color:#999; font-size:12px;"><?= substr($entry['date'], 0, 16) ?></span>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
</div>
</body>
</html>
