"""Label the existing preset library without pretending it is the current lesson."""
import re
import math

from services.academic_context import academic_context, canonical_subject

T1_CONTEXT_REVISION = 2026110901


def oscillator_equation_latex(amplitude, omega, phase):
    """Keep the displayed equation consistent with the plotted slider values."""
    from fractions import Fraction
    values = tuple(float(v) for v in (amplitude, omega, phase))
    if not all(math.isfinite(v) for v in values) or values[0] <= 0 or values[1] <= 0:
        raise ValueError('Biên độ và tần số góc phải dương, các tham số phải hữu hạn.')

    def number(value, allow_pi=False):
        if value == 0:
            return '0'
        if allow_pi:
            fraction = Fraction(value / math.pi).limit_denominator(12)
            candidate = float(fraction) * math.pi
            if fraction and abs(value - candidate) <= 2 * math.ulp(value):
                n, d = fraction.numerator, fraction.denominator
                sign = '-' if n < 0 else ''
                top = (str(abs(n)) if abs(n) != 1 else '') + r'\pi'
                return sign + (top if d == 1 else r'\frac{' + top + '}{' + str(d) + '}')
        return str(int(value)) if value.is_integer() else str(value)

    a, w, p = number(values[0]), number(values[1], True), number(values[2], True)
    return rf'x = {a}\cos\left({w}t + \left({p}\right)\right)\,\mathrm{{cm}}'



def binary_logic_state(a, b):
    """Ideal two-input Boolean model; half adder has no carry-in."""
    if any(type(v) is not int or v not in (0, 1) for v in (a, b)):
        raise ValueError('Hai đầu vào phải là bit nguyên 0 hoặc 1.')
    return dict(a=a, b=b, and_bit=a & b, or_bit=a | b, xor_bit=a ^ b,
                not_a=1-a, not_b=1-b, sum_bit=a ^ b, carry_bit=a & b,
                a_and_not_b=a & (1-b), binary_sum=f'{a & b}{a ^ b}')


def is_local_logic_command(command):
    from services.academic_context import folded
    return folded(command) == folded('Cổng logic và cộng hai bit')


def reviewed_logic_lab_request(command, subject, grade, topic):
    from services.lesson_sources import reviewed_lesson_sources
    if not is_local_logic_command(command) or canonical_subject(subject) != 'Tin học':
        return None
    review = reviewed_lesson_sources(subject, grade, topic)
    config = review.get('source_workshop', {})
    if (review['status'] != 'reviewed_requirements_source'
            or not isinstance(config, dict) or config.get('interactive_model') != 'binary_logic'):
        return None
    return dict(type='binary_logic', sources=review['sources'], scope=config['scope'])


def fixed_offset_clock(local_date, local_time, source_minutes, target_minutes):
    """Convert one instant using GIVEN offsets, never infer a city's legal zone."""
    from datetime import date, datetime, time, timedelta
    if (type(local_date) is not date or type(local_time) is not time
            or local_time.tzinfo is not None
            or any(type(v) is not int or not -720 <= v <= 840
                   for v in (source_minutes, target_minutes))):
        raise ValueError('Cần ngày/giờ hợp lệ và độ lệch UTC nguyên phút từ −720 đến +840.')
    source = datetime.combine(local_date, local_time)
    try:
        utc = source - timedelta(minutes=source_minutes)
        target = utc + timedelta(minutes=target_minutes)
    except OverflowError as error:
        raise ValueError('Kết quả vượt phạm vi ngày được hỗ trợ.') from error
    return dict(source=source, utc=utc, target=target,
                difference_minutes=target_minutes-source_minutes,
                day_change=(target.date()-source.date()).days)


def osmosis_state(inside, outside, plant=False):
    """Initial net direction for impermeant effective osmoles, equal pressure/T.

    No physical time, volume curve or lysis threshold is inferred from SGK.
    Later plant wall pressure can balance osmosis; this is not an endpoint model.
    """
    inside, outside = float(inside), float(outside)
    if any(not math.isfinite(x) or x < 0 for x in (inside, outside)):
        raise ValueError('Nồng độ phải hữu hạn và không âm.')
    delta = inside-outside
    if abs(delta) <= 1e-9:
        direction, environment = 'balanced', 'isotonic'
        result = 'Không có dòng nước thuần; nước vẫn trao đổi hai chiều.'
    elif delta > 0:
        direction, environment = 'inward', 'hypotonic'
        result = ('Nước vào ban đầu; thành tế bào tạo sức trương, áp suất tăng có thể cân bằng dòng nước.'
                  if plant else 'Nước vào ban đầu; tế bào có thể trương và vỡ tùy điều kiện, không suy ngưỡng từ mô hình này.')
    else:
        direction, environment = 'outward', 'hypertonic'
        result = ('Mất nước, giảm sức trương; đủ mất nước có thể co nguyên sinh, màng tách khỏi thành.'
                  if plant else 'Mất nước và co lại; không gọi là co nguyên sinh ở tế bào động vật.')
    return dict(direction=direction, environment=environment, delta=delta,
                result=result, bidirectional_exchange=True)


def osmosis_lab_request(command, subject, grade, topic):
    from services.academic_context import folded
    from services.lesson_sources import reviewed_lesson_sources
    if canonical_subject(subject) != 'Sinh học' or 'tham thau' not in folded(command):
        return None
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return None
    # Existing accepted lesson keeps its source; other grades opt in only through
    # an exact reviewed profile, never by inferring scope from a keyword alone.
    if review.get('id') == 'kntt-sinh10-membrane-20261107':
        return dict(type='bio_osmosis', source_url=review['sources'][0]['url'])
    model = review.get('osmosis_model')
    if not isinstance(model, dict) or not isinstance(model.get('locator'), str) or not model['locator'].strip():
        return None
    return dict(type='bio_osmosis', source_url=review['sources'][0]['url'],
                source_scope=model['locator'], source_grade=int(grade))


def reaction_rate_table_request(command, subject, grade, topic):
    """Route only the explicitly requested, reviewed H2O2 source table."""
    from services.academic_context import folded
    from services.lesson_sources import reviewed_lesson_sources
    if canonical_subject(subject) != 'Hóa học' or int(grade) != 10:
        return None
    if 'bang 19 1' not in folded(command) or 'h2o2' not in folded(command):
        return None
    review = reviewed_lesson_sources(subject, grade, topic)
    if review.get('id') != 'kntt-hoa10-tocdo-20261107' or review['status'] != 'reviewed_requirements_source':
        return None
    return {'type': 'chem_rate_table', 'times_h': [0, 3, 6, 9, 12],
            'concentrations_M': [1.000, .707, .500, .354, .250],
            'source_url': review['sources'][0]['url'], 'source_locator': 'SGK Hóa10 Bảng19.1, trang93'}


def average_reactant_rate(times, concentrations, start, end, coefficient=1):
    if (len(times) != len(concentrations) or len(times) < 2
            or not all(math.isfinite(v) for v in (*times, *concentrations, coefficient))
            or any(b <= a for a, b in zip(times, times[1:]))
            or any(c < 0 for c in concentrations) or coefficient <= 0
            or not (type(start) is int and type(end) is int and 0 <= start < end < len(times))):
        raise ValueError('Cần dữ liệu hữu hạn, thời gian tăng và hai mốc khác nhau; hệ số dương.')
    loss = (concentrations[start] - concentrations[end]) / (times[end] - times[start])
    return {'loss_rate': loss, 'normalized_rate': loss / coefficient,
            'delta_t': times[end] - times[start], 'delta_c': concentrations[end] - concentrations[start]}


def experimental_rate_ratio(no_ratio, oxygen_ratio):
    if not all(math.isfinite(x) and x >= 0 for x in (no_ratio, oxygen_ratio)):
        raise ValueError('Tỉ lệ nồng độ phải không âm, hữu hạn.')
    return no_ratio ** 2 * oxygen_ratio


def temperature_rate_ratio(gamma, low, high):
    if not all(math.isfinite(x) for x in (gamma, low, high)) or gamma <= 0:
        raise ValueError('Hệ số nhiệt độ phải dương và dữ kiện hữu hạn.')
    return gamma ** ((high - low) / 10)


def horizontal_throw_request(command, subject):
    """Use only explicit SI parameters; never substitute an unrelated preset."""
    from services.academic_context import folded
    import unicodedata
    text = ''.join(c for c in unicodedata.normalize('NFD', str(command).casefold())
                   if not unicodedata.combining(c)).replace('đ', 'd')
    if canonical_subject(subject) not in ('Vật lý', 'Khoa học tự nhiên') or 'nem ngang' not in folded(command):
        return None
    patterns = {'height': r'\bh\s*=\s*(\d+(?:[.,]\d+)?)\s*m(?![/a-z])',
                'speed': r'\bv[_ ]?0\s*=\s*(\d+(?:[.,]\d+)?)\s*m\s*/\s*s\b',
                'gravity': r'\bg\s*=\s*(\d+(?:[.,]\d+)?)\s*m\s*/\s*s(?:\^?2|²)'}
    values = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if len(matches) != 1:
            return None
        values[key] = float(matches[0].replace(',', '.'))
    if not all(math.isfinite(v) and 0 < v <= 10000 for v in values.values()):
        return None
    return dict(values, type='horizontal_throw')


def horizontal_throw_state(height, speed, gravity, fraction):
    """Ideal near-Earth motion, height measured up from a flat ground plane."""
    if (not all(math.isfinite(v) and v > 0 for v in (height, speed, gravity))
            or not math.isfinite(fraction) or not 0 <= fraction <= 1):
        raise ValueError('Cần H, v₀, g dương hữu hạn và tiến trình từ 0 đến 1.')
    total = math.sqrt(2 * height / gravity)
    t = total * fraction
    return {'T': total, 'L': speed * total, 't': t, 'x': speed * t,
            'z': max(0.0, height * (1 - fraction * fraction)),
            'vx': speed, 'vz': -gravity * t, 'speed': math.hypot(speed, gravity * t)}


def classify_closed_band(value, low, high):
    """Classify an explicit inclusive numeric band, without inferring its limits."""
    if not all(math.isfinite(v) for v in (value, low, high)) or low >= high:
        raise ValueError('Giá trị phải hữu hạn và ngưỡng dưới nhỏ hơn ngưỡng trên.')
    return 'below' if value < low else ('above' if value > high else 'within')


def soil_ph_lab_request(command, subject):
    import unicodedata
    if canonical_subject(subject) not in ('Công nghệ', 'Khoa học tự nhiên', 'Hóa học'):
        return None
    text = ''.join(c for c in unicodedata.normalize('NFD', str(command).lower())
                   if unicodedata.category(c) != 'Mn').replace('đ', 'd')
    if not ('dat' in text and re.search(r'\bph\b', text)):
        return None
    match = re.search(r'trung tinh\s+tu\s+(\d+(?:[.,]\d+)?)\s+den\s+(\d+(?:[.,]\d+)?)', text)
    if not match:
        return None
    low, high = (float(v.replace(',', '.')) for v in match.groups())
    if not 0 <= low < high <= 14:
        return None
    return {'type': 'soil_ph_band', 'low': low, 'high': high}


def is_proposition_request(command, subject):
    from services.academic_context import folded
    return canonical_subject(subject) == 'Toán học' and 'menh de' in folded(command)


def proposition_lab_request(command, subject):
    """Route a supported explicit predicate task by intent, not polynomial shape.

    Parse a limited numeric quadratic equality, never arbitrary Python/code.
    Unknown expressions are left unsupported rather than replaced by a sample.
    """
    from fractions import Fraction
    if not is_proposition_request(command, subject):
        return None
    compact = re.sub(r'\s+', ' ', str(command)).replace('−', '-').replace('²', '^2')
    compact = re.sub(r'\s*([+*/^=\-])\s*', r'\1', compact)
    number = r'\d+(?:\.\d+)?'
    match = re.search(r'(?<![\w./*^+\-])(?P<a>[+-]?(?:' + number + r'\*?)?)x\^2'
                      r'(?P<b>[+-](?:' + number + r'\*?)?)x'
                      r'(?P<c>[+-]' + number + r')=0', compact)
    if not match:
        return None
    def coefficient(value):
        value = value.replace('*', '')
        return str(Fraction({'': '1', '+': '1', '-': '-1'}.get(value, value)))
    return dict(type='proposition_quadratic', **{k: coefficient(match[k]) for k in ('a', 'b', 'c')})


def evaluate_proposition(data, value):
    """Exact rational substitution; a false proposition remains a proposition."""
    from fractions import Fraction
    if not re.fullmatch(r'[+-]?\d+(?:\.\d+|/\d+)?', str(value).strip()):
        raise ValueError('Nhập số nguyên, số thập phân hoặc phân số, ví dụ 1/2.')
    x = Fraction(str(value).strip())
    result = Fraction(data['a']) * x*x + Fraction(data['b']) * x + Fraction(data['c'])
    return result, result == 0


def function_formula_latex(numerator, denominator=None):
    """Format selected coefficients exactly, omitting zero terms and +- signs."""
    import sympy as sp
    x = sp.Symbol('x')
    def polynomial(coefficients):
        return sum(sp.Rational(str(value)) * x**power
                   for power, value in enumerate(reversed(coefficients)))
    top = sp.latex(polynomial(numerator))
    if denominator is None:
        return 'y = ' + top
    return r'y = \frac{' + top + '}{' + sp.latex(polynomial(denominator)) + '}'


def lesson_context_examples(subject, grade, topics):
    """Use selected-grade suggestions; never substitute senior-grade examples."""
    subject, grade = academic_context(subject, grade)
    examples = [re.sub(r'^Chuyên đề\s*\d+\s*:\s*', '', str(t)).strip() for t in topics[:2]]
    return 'Ví dụ: ' + '; '.join(examples) if examples else f'Nhập tên bài môn {subject} lớp {grade} và dữ kiện cần học.'


def ideal_ph(log_h):
    """Dilute ideal aqueous model at 25 C; activity approximated by c/c0."""
    value = float(log_h)
    if not math.isfinite(value) or not -14 <= value <= 0:
        raise ValueError('Mẫu pH hỗ trợ log10([H+]/c0) từ -14 đến 0.')
    return dict(ph=-value, log_h=value, log_oh=-14-value,
                h=10**value, oh=10**(-14-value))


def logarithm_model(base, coefficient, vertical_shift, natural=False):
    """Validate and describe y=k*log_a(x)+c without silently changing inputs."""
    base, coefficient, vertical_shift = map(float, (base, coefficient, vertical_shift))
    if not all(math.isfinite(value) for value in (base, coefficient, vertical_shift)):
        raise ValueError('Các tham số phải là số hữu hạn.')
    if natural:
        base = math.e
    elif base <= 0 or math.isclose(base, 1.0, abs_tol=1e-12):
        raise ValueError('Cơ số a phải dương và khác 1.')
    if coefficient == 0:
        behavior = 'constant'
    elif (coefficient > 0) == (base > 1):
        behavior = 'increasing'
    else:
        behavior = 'decreasing'
    return dict(base=base, coefficient=coefficient, vertical_shift=vertical_shift,
                behavior=behavior, has_vertical_asymptote=(coefficient != 0),
                constant_value=vertical_shift if coefficient == 0 else None)


def ammonia_equilibrium(temp_c, pressure_bar):
    """Ideal gas N2+3H2=2NH3; initial mole amounts 1:3:0; p0=1 bar.

    Shomate coefficients: NIST Chemistry WebBook, Chase (1998).
    https://webbook.nist.gov/cgi/cbook.cgi?ID=C7664417&Mask=1
    https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1
    https://webbook.nist.gov/cgi/cbook.cgi?ID=1333-74-0&cTG=on
    This is an ideal equilibrium model, not industrial yield or reaction rate.
    """
    temperature, pressure = float(temp_c)+273.15, float(pressure_bar)
    if not math.isfinite(temperature) or not 298.15 <= temperature <= 1000 or not math.isfinite(pressure) or pressure <= 0:
        raise ValueError('Ngoài miền nhiệt độ NIST hoặc áp suất không dương.')
    nh3 = (19.99563, 49.77119, -15.37599, 1.921168, .189174, -53.30667, 203.8591)
    h2 = (33.066178, -11.363417, 11.432816, -2.772874, -.158558, -9.980797, 172.707974)
    n2 = ((28.98641, 1.853978, -9.647459, 16.63537, .000117, -8.671914, 226.4168)
          if temperature < 500 else (19.50583, 19.88705, -8.598535, 1.369784, .527601, -4.935202, 212.3900))
    t = temperature/1000

    def hs(coefficients):
        a,b,c,d,e,f,g = coefficients
        # Formation enthalpy is included: Shomate (H-H298) + Hf298.
        h = 1000*(a*t + b*t*t/2 + c*t**3/3 + d*t**4/4 - e/t + f)
        s = a*math.log(t) + b*t + c*t*t/2 + d*t**3/3 - e/(2*t*t) + g
        return h, s

    properties = [hs(coefficients) for coefficients in (nh3, n2, h2)]
    dh, ds = [2*properties[0][i]-properties[1][i]-3*properties[2][i] for i in (0,1)]
    log_kp = -(dh-temperature*ds)/(8.31446261815324*temperature)
    lo, hi = 0.0, 1.0
    for _ in range(70):
        extent = (lo+hi)/2
        if extent >= 1:
            break
        log_q = math.log(4)+2*math.log(extent)+2*math.log(4-2*extent)-math.log(27)-4*math.log1p(-extent)-2*math.log(pressure)
        if log_q < log_kp:
            lo = extent
        else:
            hi = extent
    extent = (lo+hi)/2
    return dict(extent=extent, conversion=100*extent, nh3_mole_fraction=2*extent/(4-2*extent), kp=math.exp(log_kp))


def resolve_preset_lab(subject, label, payload):
    """Correct one mismatched preset; keep its menu identity and other payloads."""
    subject = canonical_subject(subject)
    if subject in ('Hóa học', 'Khoa học tự nhiên') and 'pH' in label:
        return {'type': 'chem_ph', 'log_h': -7.0}
    if (subject == 'Tin học'
            and label == 'Sơ đồ thuật toán & Cây nhị phân'
            and payload.get('type') == 'oxyz'):
        return {'type': 'mermaid', 'code': '''graph TD
R["Mẫu minh họa: tìm kiếm trên cây nhị phân tìm kiếm"] --> T["Cây mẫu"]
T --> N8["8"]
N8 --> N3["Nhánh trái: 3"]
N8 --> N10["Nhánh phải: 10"]
N3 --> N1["Nhánh trái: 1"]
N3 --> N6["Nhánh phải: 6"]
R --> A["Thuật toán: bắt đầu tại gốc, so sánh k với khóa nút"]
A --> E["Nút rỗng: kết luận không tìm thấy"]
A --> F["k bằng khóa: tìm thấy, dừng"]
A --> L["k nhỏ hơn khóa: sang con trái và lặp lại"]
A --> G["k lớn hơn khóa: sang con phải và lặp lại"]'''}
    return dict(payload)


def preset_lab_label(label, subject, grade):
    _, grade = academic_context(subject, grade)
    value = str(label)
    # Keep preset keys/payloads stable for saved sessions while correcting what
    # the rendered menu claims each generic visualization actually represents.
    honest_labels = {
        'Mã hóa dữ liệu (RSA)': 'Đồ thị hàm mũ minh họa (không mô phỏng mã hóa RSA)',
        'Mô hình mạng tinh thể': 'Điểm tọa độ Oxyz minh họa (không phải mô hình mạng tinh thể)',
        'Mạch điện xoay chiều RLC & Dao động': 'Mô hình dao động cơ (không mô phỏng mạch RLC)',
        'Tăng trưởng giới hạn': 'Đồ thị logarit cơ bản (không phải mô hình tăng trưởng giới hạn)',
        'Quy luật di truyền Mendel (KHTN)': 'Mô hình lai Aa × Aa (chỉ xét trội hoàn toàn)',
    }
    for misleading, accurate in honest_labels.items():
        if misleading in value:
            value = value.replace(misleading, accurate)
    if canonical_subject(subject) == 'Khoa học tự nhiên' and 'pH' in value:
        value = value.replace('(KHTN)', '(KNTT 8)')
    match = re.search(r'(?:KNTT|Vật l[íý]|Hóa học|Sinh học)\s*(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?', value, re.I)
    # Existing grade annotations are descriptions supplied with the preset,
    # not a verified curriculum map. Never invent a grade for untagged tools.
    if match:
        first, last = int(match[1]), int(match[2] or match[1])
        grades = f'{first}–{last}' if first != last else str(first)
        prefix = f'Mẫu tham khảo, nhãn lớp {grades}' if first <= grade <= last else f'Mở rộng, nhãn lớp {grades}'
    else:
        prefix = 'Công cụ minh họa'
    body = re.sub(r'\(\s*KNTT\s*\d{1,2}(?:\s*[-–]\s*\d{1,2})?\s*\)', '', value, flags=re.I).strip()
    return f'[{prefix}] {body}'


def preset_lab_note(subject, grade):
    subject, grade = academic_context(subject, grade)
    return (f'Thư viện mẫu minh họa độc lập với bài {subject} lớp {grade} đang học. '
            'Giữ các công cụ mở rộng; nhãn lớp lấy từ cấu hình mẫu, chưa phải đối chiếu SGK. '
            'Mẫu có sẵn không tự lấy hàm số hoặc dữ kiện từ bài học. '
            'Muốn mô phỏng theo bài, hãy nêu rõ dữ kiện trong lệnh mô phỏng bên dưới.')


def is_local_workshop_command(command):
    from services.academic_context import folded
    return folded(command) == 'doi chieu tu lieu theo bai hoc'


def reviewed_workshop_request(command, subject, grade, topic):
    """Route an explicit source-comparison workshop without a model call."""
    from copy import deepcopy
    from services.academic_context import folded
    from services.lesson_sources import reviewed_lesson_sources
    if not is_local_workshop_command(command):
        return None
    review = reviewed_lesson_sources(subject, grade, topic)
    config = review.get('source_workshop')
    if review['status'] != 'reviewed_requirements_source' or not isinstance(config, dict):
        return None
    cards, questions = config.get('cards'), config.get('questions')
    if (not isinstance(config.get('title'), str) or not isinstance(cards, list)
            or not 2 <= len(cards) <= 6 or not isinstance(questions, list)
            or not 1 <= len(questions) <= 6):
        return None
    if any(not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip()
                                            for k in ('title', 'text')) for c in cards):
        return None
    for question in questions:
        if (not isinstance(question, dict) or not isinstance(question.get('prompt'), str)
                or not isinstance(question.get('options'), list)
                or not 2 <= len(question['options']) <= 6
                or not all(isinstance(x, str) and x.strip() for x in question['options'])
                or type(question.get('correct')) is not int
                or not 0 <= question['correct'] < len(question['options'])
                or not isinstance(question.get('feedback'), str)):
            return None
    return dict(type='source_workshop', workshop=deepcopy(config),
                sources=deepcopy(review['sources']), review_id=review['id'])


def evaluate_source_workshop(questions, choices):
    """Return feedback only after every practice choice is provided."""
    if len(questions) != len(choices) or any(type(x) is not int or
            not 0 <= x < len(q['options']) for q, x in zip(questions, choices)):
        raise ValueError('Hãy chọn nhận xét cho tất cả câu trước khi đối chiếu.')
    correct = [choice == question['correct'] for question, choice in zip(questions, choices)]
    return dict(score=sum(correct), total=len(correct), correct=correct,
                feedback=[q['feedback'] for q in questions])
