#!/usr/bin/env node
/**
 * volume_calculator.js - Калькулятор объёма тел на JavaScript (Node.js CLI + веб)
 * CLI: node volume_calculator.js
 * Веб: откройте как HTML
 */
const fs = require('fs');
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const PI = Math.PI;
const HISTORY_FILE = 'volume_history.json';

const shapes = {
    '1': { name: 'Куб', func: (p) => p[0] ** 3, params: ['сторону'] },
    '2': { name: 'Шар', func: (p) => 4/3 * PI * p[0] ** 3, params: ['радиус'] },
    '3': { name: 'Цилиндр', func: (p) => PI * p[0] ** 2 * p[1], params: ['радиус', 'высоту'] },
    '4': { name: 'Конус', func: (p) => 1/3 * PI * p[0] ** 2 * p[1], params: ['радиус', 'высоту'] },
    '5': { name: 'Параллелепипед', func: (p) => p[0] * p[1] * p[2], params: ['длину', 'ширину', 'высоту'] },
    '6': { name: 'Пирамида', func: (p) => 1/3 * p[0] * p[1], params: ['площадь основания', 'высоту'] },
    '7': { name: 'Призма', func: (p) => p[0] * p[1], params: ['площадь основания', 'высоту'] },
    '8': { name: 'Тор', func: (p) => 2 * PI ** 2 * p[0] * p[1] ** 2, params: ['большой радиус', 'малый радиус'] },
    '9': { name: 'Эллипсоид', func: (p) => 4/3 * PI * p[0] * p[1] * p[2], params: ['полуось a', 'полуось b', 'полуось c'] },
    '10': { name: 'Усечённый конус', func: (p) => 1/3 * PI * p[2] * (p[0] ** 2 + p[0] * p[1] + p[1] ** 2), params: ['радиус 1', 'радиус 2', 'высоту'] },
};

function prompt(query) {
    return new Promise(resolve => rl.question(query, resolve));
}

function saveHistory(entry) {
    let history = [];
    if (fs.existsSync(HISTORY_FILE)) {
        try {
            history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
        } catch {}
    }
    history.push(entry);
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

function loadHistory() {
    if (fs.existsSync(HISTORY_FILE)) {
        try {
            return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
        } catch {}
    }
    return [];
}

function exportCSV(filename) {
    const history = loadHistory();
    if (!history.length) {
        console.log('История пуста.');
        return;
    }
    const lines = ['Дата,Фигура,Параметры,Объём,Единицы'];
    history.forEach(e => {
        lines.push(`${e.date.slice(0,19)},${e.shape},"${e.params}",${e.result},${e.units || 'куб. ед.'}`);
    });
    fs.writeFileSync(filename, lines.join('\n'), 'utf8');
    console.log(`Экспортировано в ${filename}`);
}

async function interactiveCLI() {
    console.log('📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ');
    let history = loadHistory();
    let units = 'куб. ед.';

    while (true) {
        console.log('\nВыберите фигуру:');
        for (const [key, shape] of Object.entries(shapes)) {
            console.log(`${key}. ${shape.name}`);
        }
        console.log('h. Показать историю');
        console.log('e. Экспорт CSV');
        console.log('u. Сменить единицы');
        console.log('0. Выход');

        const choice = await prompt('Ваш выбор: ');

        if (choice === '0') break;
        else if (choice.toLowerCase() === 'h') {
            if (!history.length) {
                console.log('История пуста.');
            } else {
                console.log('\n=== ИСТОРИЯ ===');
                history.slice(-10).forEach(e => {
                    console.log(`${e.date.slice(0,19)} | ${e.shape} | ${e.result}`);
                });
            }
            continue;
        } else if (choice.toLowerCase() === 'e') {
            const filename = await prompt('Имя CSV файла (по умолчанию volume_history.csv): ') || 'volume_history.csv';
            exportCSV(filename);
            continue;
        } else if (choice.toLowerCase() === 'u') {
            console.log('Доступные единицы: куб. ед., см³, м³, дм³, л, in³');
            const input = await prompt('Выберите единицы: ');
            if (input) units = input;
            continue;
        } else if (shapes[choice]) {
            const shape = shapes[choice];
            const params = [];
            console.log(`\nФигура: ${shape.name}`);
            for (const pname of shape.params) {
                while (true) {
                    const input = await prompt(`Введите ${pname}: `);
                    const val = parseFloat(input);
                    if (!isNaN(val) && val > 0) {
                        params.push(val);
                        break;
                    }
                    console.log('Введите положительное число.');
                }
            }
            const result = shape.func(params);
            const resultStr = `${result.toFixed(4)} ${units}`;
            console.log(`\nОбъём ${shape.name.toLowerCase()}: ${resultStr}`);

            const save = await prompt('Сохранить результат? (y/n): ');
            if (save.toLowerCase() === 'y') {
                const entry = {
                    date: new Date().toISOString(),
                    shape: shape.name,
                    params: params.join(', '),
                    result: resultStr,
                    units: units
                };
                saveHistory(entry);
                history.push(entry);
                console.log('✅ Сохранено!');
            }
        } else {
            console.log('Неверный выбор.');
        }
    }
    rl.close();
}

if (require.main === module) {
    interactiveCLI().catch(console.error);
}

// ========== Браузерная версия (для веб-интерфейса) ==========
if (typeof window !== 'undefined') {
    window.shapes = shapes;
    window.calculateVolume = function(shapeKey, params) {
        if (!shapes[shapeKey]) return null;
        return shapes[shapeKey].func(params);
    };
}
