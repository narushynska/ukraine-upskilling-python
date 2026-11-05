"""Дати в Pandas: тип datetime64 і як з ним працювати.

AI Programming in Python · сесія підтримки 3.

Файл у форматі «клітинок» (# %%): у VS Code над кожним блоком з'являється
кнопка Run Cell, тож можна виконувати по одній клітинці, як у Jupyter.
Поруч мають лежати service_requests.csv і food_waste_dataset.csv з теми 3
(якщо service_requests.csv немає, код створить таблицю сам).
"""

# %% [markdown]
# # Дати в Pandas: тип `datetime64` і як з ним працювати
#
# **Сесія підтримки 3 · AI Programming in Python.** Цей файл пояснює одну річ: чому дата з CSV спочатку «просто текст» і як зробити її справжньою датою.
#
# **Як працювати:** запускайте клітинки по черзі (у VS Code: Shift+Enter або Run Cell). Читайте пояснення над кожною клітинкою і передбачайте результат до запуску.
#
# **Що потрібно:** pandas (3.x) і файли `service_requests.csv`, `food_waste_dataset.csv` з теми 3 поруч із цим файлом. Якщо `service_requests.csv` не знайдено, ноутбук створить маленьку таблицю сам.

# %% [markdown]
# ## 0. Головна ідея за 30 секунд
#
# - У Pandas **немає окремого типу `date`**. Дата і час разом називаються **`datetime64`**. Одна окрема дата-час називається **`Timestamp`**.
# - Коли `read_csv` читає файл, дата приходить як **текст** (`str`), бо CSV не знає, що це дата.
# - Текст **не вміє** рахувати дні, сортуватися за календарем чи групуватися за місяцями. Тому дату треба **перетворити**: `pd.to_datetime(...)`.
# - Після перетворення працює **`.dt`**: `.dt.year`, `.dt.month`, `.dt.day_name()`, віднімання дат тощо.

# %%
import pandas as pd
import datetime

print("pandas", pd.__version__)

# %% [markdown]
# ## 1. Дата в Python і дата в Pandas: чотири різні речі

# %%
d1 = datetime.date(2026, 11, 3)            # звичайна дата Python (без часу)
d2 = pd.Timestamp("2026-11-03 18:30")      # одна дата й час у Pandas
col = pd.Series(pd.to_datetime(["2026-11-03", "2026-11-10"]))   # стовпець дат

print("datetime.date :", d1, type(d1).__name__)
print("Timestamp     :", d2, type(d2).__name__)
print("тип стовпця   :", col.dtype)

# %% [markdown]
# Тип стовпця виглядає як `datetime64[us]` (у старіших версіях Pandas було `datetime64[ns]`, різниця лише в точності: мікросекунди чи наносекунди). Для нас важливо одне: **`datetime64` = справжні дати**.
#
# | Що | Де живе | Приклад |
# |---|---|---|
# | `datetime.date` | чистий Python | `datetime.date(2026, 11, 3)` |
# | `Timestamp` | одна дата-час у Pandas | `pd.Timestamp("2026-11-03")` |
# | `datetime64` | **стовпець** дат у таблиці | `df["request_date"]` після перетворення |
# | `str` (текст) | те, що дає `read_csv` | `"2026-11-03"` |

# %% [markdown]
# ## 2. Дані: дата з CSV приходить як текст

# %%
try:
    requests = pd.read_csv("service_requests.csv")
except FileNotFoundError:
    # запасний варіант: та сама таблиця прямо в коді
    from io import StringIO
    requests = pd.read_csv(StringIO(
        "request_id,city,service,request_date,wait_days\n"
        "101,Київ,Юридична допомога,2026-09-01,5\n"
        "102,Львів,Курси мови,2026-09-02,7\n"
        "103,Київ,Психологічна підтримка,2026-09-02,3\n"
        "104,Одеса,Курси мови,2026-09-03,10\n"
        "105,Харків,Юридична допомога,2026-09-05,4\n"
    ))

print(requests[["request_id", "request_date", "wait_days"]].head())

# %%
requests.info()

# %% [markdown]
# У колонці `Dtype` біля `request_date` стоїть **`str`** (у Pandas 2 було б `object`). Це **текст**, а не дата. Перевіримо, що з цим не так.

# %% [markdown]
# ## 3. Чому текстова дата небезпечна

# %%
# Текст можна "відняти"? Спробуємо:
try:
    requests["request_date"].iloc[3] - requests["request_date"].iloc[0]
except Exception as e:
    print("Помилка:", type(e).__name__, "-", e)

# %% [markdown]
# Так, помилка. Тепер найковарніше: **текст сортується за літерами, а не за календарем**. У форматі `рік-місяць-день` це випадково працює, а в нашому `ДД.ММ.РРРР` ні.

# %%
text_dates = pd.Series(["10.01.2026", "02.03.2025", "25.12.2024"])
print("Як текст (за літерами):")
print(text_dates.sort_values().tolist())

real_dates = pd.to_datetime(text_dates, format="%d.%m.%Y")
print("Як дати (за календарем):")
print(real_dates.sort_values().dt.strftime("%d.%m.%Y").tolist())

# %% [markdown]
# Видно: як текст найранішою «стала» `02.03.2025`, а справді найраніша `25.12.2024` опинилась в кінці. Текст дивиться на перші цифри (день), а не на рік. Саме тому дату завжди перетворюємо.

# %% [markdown]
# ## 4. `pd.to_datetime`: перетворення тексту на дату

# %%
requests["date"] = pd.to_datetime(requests["request_date"])

print(requests["date"].dtype)
print(requests[["request_date", "date"]].head(3))

# %% [markdown]
# Тепер тип **`datetime64[us]`**. Виглядає так само, але це вже справжня дата: працює календар.
#
# ### 4.1 Свій формат: параметр `format`
#
# Якщо дата записана не як `2026-11-03`, **скажіть Pandas формат**. Найпоширеніші коди:
#
# | Код | Значення | Приклад |
# |---|---|---|
# | `%d` | день, 2 цифри | `03` |
# | `%m` | місяць, 2 цифри | `11` |
# | `%Y` | рік, 4 цифри | `2026` |
# | `%H:%M` | година:хвилина | `18:30` |
#
# Тобто `03.11.2026` = `"%d.%m.%Y"`.

# %%
print(pd.to_datetime("03.11.2026", format="%d.%m.%Y"))

# %% [markdown]
# ### 4.2 Пастка: 03/11/2026 це 3 листопада чи 11 березня?
#
# В Україні спершу день, в США спершу місяць. Pandas за замовчуванням вважає, що **спершу місяць**. Тому для наших дат пишіть або `format`, або `dayfirst=True`.

# %%
x = "03/11/2026"
print("як в США (%m/%d):", pd.to_datetime(x, format="%m/%d/%Y").date(), "(місяць перший)")
print("dayfirst=True   :", pd.to_datetime(x, dayfirst=True).date(), "(день перший)")
print("format %d/%m/%Y :", pd.to_datetime(x, format="%d/%m/%Y").date())

# %% [markdown]
# **Порада:** найнадійніше завжди вказувати `format=`. Тоді немає здогадок, і помилки видно одразу.

# %% [markdown]
# ### 4.3 Погані дати: `errors="coerce"` і `NaT`
#
# У реальних даних трапляється сміття: порожнє поле, `31.02.2026`, `невідомо`. За замовчуванням Pandas зупиняється з помилкою. З `errors="coerce"` погані значення стають **`NaT`** («not a time», пропуск для дат, як `NaN` для чисел).

# %%
messy = pd.Series(["03.11.2026", "31.02.2026", "невідомо", None, "10.11.2026"])

try:
    pd.to_datetime(messy, format="%d.%m.%Y")
except Exception as e:
    print("Без coerce:", type(e).__name__)

clean = pd.to_datetime(messy, format="%d.%m.%Y", errors="coerce")
print()
print(clean)
print("Скільки поганих дат:", clean.isna().sum())

# %% [markdown]
# `NaT` ми не ховаємо мовчки: рахуємо (`isna().sum()`), дивимось, що саме було не так, і записуємо рішення (це частина домашнього завдання про якість даних).

# %% [markdown]
# ## 5. Читати дати одразу: `parse_dates`

# %%
try:
    requests2 = pd.read_csv("service_requests.csv", parse_dates=["request_date"])
    print(requests2["request_date"].dtype)
except FileNotFoundError:
    print("service_requests.csv не знайдено поруч: пропустіть цю клітинку")

# %% [markdown]
# `parse_dates=[...]` перетворює колонку одразу під час читання, окремий `to_datetime` не потрібен. Працює для формату `РРРР-ММ-ДД`; для інших форматів лишається `to_datetime(..., format=...)`.

# %% [markdown]
# ## 6. Акселератор `.dt`: що можна дізнатися з дати

# %%
dates = pd.to_datetime(requests["request_date"])

parts = pd.DataFrame({
    "дата": dates,
    "рік": dates.dt.year,
    "місяць": dates.dt.month,
    "день": dates.dt.day,
    "день_тижня_0_пн": dates.dt.day_of_week,
    "назва_англ": dates.dt.day_name(),
})
print(parts.head(5))

# %% [markdown]
# Шпаргалка `.dt`:
#
# | Вираз | Що дає |
# |---|---|
# | `.dt.year`, `.dt.month`, `.dt.day` | числа |
# | `.dt.day_of_week` | 0 = понеділок … 6 = неділя |
# | `.dt.day_name()` | назва дня англійською |
# | `.dt.to_period("M")` | «місяць» для групування |
# | `.dt.strftime("%d.%m.%Y")` | **назад у текст** у потрібному вигляді |
# | `.dt.date` | звичайні дати Python (тип стає `object`, для обчислень не потрібно) |

# %%
# Українські назви днів: словник робить результат незалежним від мови Windows
uk_days = {0: "понеділок", 1: "вівторок", 2: "середа", 3: "четвер",
           4: "пʼятниця", 5: "субота", 6: "неділя"}

requests["день_тижня"] = dates.dt.day_of_week.map(uk_days)
requests["дата_для_людей"] = dates.dt.strftime("%d.%m.%Y")
print(requests[["request_date", "день_тижня", "дата_для_людей"]].head(4))

# %% [markdown]
# ## 7. Арифметика: різниця дат це `Timedelta`

# %%
start = pd.Timestamp("2026-11-03")
end = pd.Timestamp("2026-11-10")

gap = end - start
print(gap, "| тип:", type(gap).__name__)
print("днів:", gap.days)

print("через 14 днів:", (start + pd.Timedelta(days=14)).date())

# %%
# Для всього стовпця: від найранішої заявки до кожної
first = dates.min()
requests["днів_від_першої"] = (dates - first).dt.days
print("Діапазон:", dates.min().date(), "-", dates.max().date(), "=", (dates.max() - dates.min()).days, "днів")
print(requests[["request_date", "днів_від_першої"]].head(5))

# %%
# Послідовність дат з нуля
print(pd.date_range("2026-11-03", periods=5, freq="D"))

# %% [markdown]
# ## 8. Фільтри й групування за датами

# %%
# Заявки з 3 по 5 вересня включно
mask = (dates >= "2026-09-03") & (dates <= "2026-09-05")
print(requests.loc[mask, ["request_id", "request_date", "service"]])

# %%
# Для групування за місяцями потрібен набір із довшим періодом: Food Waste (2025)
try:
    fw = pd.read_csv("food_waste_dataset.csv", parse_dates=["Date"])
    print("тип Date:", fw["Date"].dtype)
    print("період:", fw["Date"].min().date(), "-", fw["Date"].max().date())

    by_month = (fw.groupby(fw["Date"].dt.to_period("M"))["Waste_Quantity"]
                  .mean().round(2))
    print()
    print("Середня кількість відходів за місяцями:")
    print(by_month)
except FileNotFoundError:
    print("food_waste_dataset.csv не знайдено поруч із цим файлом: пропустіть клітинку")

# %% [markdown]
# Усе це стало можливим лише після того, як `Date` перестала бути текстом.

# %% [markdown]
# ## 9. Типові помилки (перевірте себе)
#
# 1. **Забули перетворити.** `df["date"].dt.year` дає `AttributeError: Can only use .dt accessor with datetimelike values`. Це означає: колонка ще текст. Виправлення: `pd.to_datetime(...)`.
# 2. **Не вказали формат.** `03.11.2026` може прочитатись як 11 березня. Виправлення: `format="%d.%m.%Y"`.
# 3. **Поганих дат нема в підрахунку.** З `errors="coerce"` вони тихо стали `NaT`. Виправлення: `isna().sum()` і запис рішення.
# 4. **`.dt.date` для обчислень.** Він повертає звичайні дати Python, а не `datetime64`: віднімання й `.dt` далі не працюють. Лишайтеся на `datetime64`, а `date` беріть лише для показу.

# %%
# Приклад помилки №1: .dt на тексті
try:
    requests["request_date"].dt.year
except AttributeError as e:
    print("AttributeError:", e)

# %% [markdown]
# ## 10. Міні-завдання
#
# Виконайте в нових клітинках і перевірте, що відповіді мають сенс:
#
# 1. Створіть `pd.to_datetime(["15.11.2026", "01.12.2026"], format="%d.%m.%Y")`. Який це тип?
# 2. Скільки днів між 3 листопада 2026 і 31 грудня 2026?
# 3. У `food_waste_dataset.csv` знайдіть **день тижня**, у який у середньому найбільше `Waste_Quantity`. Підказка: `fw["Date"].dt.day_of_week` у `groupby`.
# 4. Поясніть одним реченням, чому `"02.03.2026" > "10.01.2026"` для тексту дає `False`, а для справжніх дат (2 березня проти 10 січня) дає `True`. Перевірте обидва варіанти кодом.
#
# ## Підсумок
#
# - CSV дає дату як **текст**: це нормально, але з нею нічого не порахуєш.
# - `pd.to_datetime(колонка, format="%d.%m.%Y")` перетворює на **`datetime64`**, поганих значень не ховаємо (`errors="coerce"` + `isna().sum()`).
# - `.dt` дає рік, місяць, день тижня; різниця дат дає `Timedelta`; `groupby(.dt.to_period("M"))` групує за місяцями.
#
# **Посилання:**
# [pd.to_datetime](https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html) ·
# [Series.dt](https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.html) ·
# [Time series (user guide)](https://pandas.pydata.org/docs/user_guide/timeseries.html) ·
# [коди формату %d %m %Y](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
