import csv
import os
import difflib
import random
import time
from datetime import datetime
import json


# === CONFIG ===
CSV_FILE = 'vocab.csv'

CONFIG_FILE = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"language": "English", "user_level": 1}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
def log_history(action, word, category, language):
    file_exists = os.path.exists("history.csv")
    with open("history.csv", mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['action', 'timestamp', 'word', 'category', 'language']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'action': action,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'word': word,
            'category': category,
            'language': language
        })
# === FUNCTION: Check if word exists ===
def word_exists(word, file_path=CSV_FILE):
    if not os.path.exists(file_path):
        return False
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['word'].strip().lower() == word.strip().lower():
                return True
    return False

# === FUNCTION: Add new word ===
def add_new_word_with_check():
    word = input("\nNhập từ mới: ").strip()
    if word_exists(word):
        print(f"⚠️ Từ '{word}' đã tồn tại trong dữ liệu.")
        choice = input("👉 Bạn có muốn bổ sung thêm nghĩa và ví dụ không? (y/n): ").strip().lower()
        if choice == 'y':
            updated = False
            with open(CSV_FILE, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                vocab = list(reader)

            for row in vocab:
                if row['word'].strip().lower() == word.lower():
                    # Bổ sung nghĩa nếu chưa có
                    new_meaning = input(f"👉 Nhập nghĩa bổ sung (để trống nếu không): ").strip()
                    if new_meaning and new_meaning.lower() not in row['meaning'].lower():
                        row['meaning'] += f" | {new_meaning}"
                        updated = True

                    # Bổ sung ví dụ nếu chưa có
                    new_example = input(f"👉 Nhập ví dụ bổ sung (để trống nếu không): ").strip()
                    if new_example and new_example not in row['example']:
                        row['example'] += f"\n- {new_example}"
                        updated = True

            if updated:
                fieldnames = ['word', 'meaning', 'phonetic', 'language', 'review_count', 'last_review',
              'is_mastered', 'last_result', 'example', 'type', 'category', 'level']
                with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows([
                       {k: row.get(k, '') for k in fieldnames}
                       for row in vocab
                    ])
                print("✅ Đã cập nhật thêm nghĩa/ví dụ.")
            else:
                print("ℹ️ Không có nội dung nào được cập nhật.")
        return  # Dừng lại sau khi cập nhật

    # Trường hợp từ chưa có, tiến hành thêm mới
    meaning = input("Nhập nghĩa của từ: ").strip()
    phonetic = input("Nhập phiên âm (nếu có): ").strip()
    language = input("Ngôn ngữ (English/Korean): ").strip().capitalize()
    type_ = input("Loại từ (noun/verb/adj...): ").strip().lower()
    category = input("Chủ đề từ (food/color/action...): ").strip().lower()
    example = input("Nhập ví dụ sử dụng từ này: ").strip()

    print("\n📊 Gợi ý cấp độ từ vựng:")
    print("1 – Starter: từ cơ bản, dễ, quen thuộc (ví dụ: cat, run, blue)")
    print("2 – Beginner: từ đơn giản, thường gặp trong giao tiếp")
    print("3 – Pre-Intermediate: từ thông dụng hơn, dùng trong câu mô tả")
    print("4 – Intermediate: từ trừu tượng hoặc ít phổ biến hơn")
    print("5 – Advanced: từ học thuật, phức tạp hoặc ít xuất hiện")
    level = input("Cấp độ từ này (1–5): ").strip()
    if level not in ['1', '2', '3', '4', '5']:
        print("❌ Cấp độ không hợp lệ. Vui lòng nhập số từ 1 đến 5.")
        return

    new_entry = {
        'word': word,
        'meaning': meaning,
        'phonetic': phonetic,
        'language': language,
        'review_count': '0',
        'last_review': datetime.today().strftime('%Y-%m-%d'),
        'is_mastered': 'False',
        'last_result': '',
        'example': example,
        'type': type_,
        'category': category,
        'level': level
    }

    fieldnames = ['word', 'meaning', 'phonetic', 'language', 'review_count', 'last_review',
                  'is_mastered', 'last_result', 'example', 'type', 'category', 'level']
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_entry)

    print(f"✅ Đã thêm từ mới: {word} – {meaning}")

# === FUNCTION: Tính độ ưu tiên từ cần ôn ===
def calculate_priority(word_data):
    if word_data.get("is_mastered", "False") == "True":
        return 0

    try:
        last_review_str = word_data.get("last_review", "").strip()
        if not last_review_str:
            return 0
        last_review_date = datetime.strptime(last_review_str, "%Y-%m-%d")
        days_since = (datetime.today() - last_review_date).days
    except Exception as e:
        print(f"⚠️ Lỗi định dạng ngày với từ: {word_data.get('word', '')}. Bỏ qua.")
        return 0

    try:
        count = int(word_data.get("review_count", "0"))
    except:
        count = 0

    priority = days_since + (5 - count) * 2
    if word_data.get("last_result", "") == "wrong":
        priority += 10
    return priority

# === FUNCTION: Gợi ý các từ cần ôn ===
def get_words_to_review(language_filter=None, user_level=5, file_path=CSV_FILE, top_n=10):
    if not os.path.exists(file_path):
        return []

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        vocab_list = []
        for row in reader:
            level_str = row.get('level', '').strip()
            if not level_str.isdigit():
                continue  # Bỏ qua nếu không phải số
            level = int(level_str)

            if language_filter in [None, '', 'All', row['language']] and level <= user_level:
                row['priority'] = calculate_priority(row)
                vocab_list.append(row)

    sorted_words = sorted(vocab_list, key=lambda x: -x['priority'])
    return sorted_words[:top_n]

# === FUNCTION: Cập nhật trạng thái từ sau khi ôn ===
def update_word(word_data, correct):
    word_data['review_count'] = str(int(word_data['review_count']) + 1)
    word_data['last_review'] = datetime.today().strftime("%Y-%m-%d")
    word_data['is_mastered'] = 'True' if correct else 'False'
    word_data['last_result'] = 'correct' if correct else 'wrong'
    return word_data

# === FUNCTION: Lưu danh sách sau khi ôn ===
def save_vocab_list(vocab_list, file_path=CSV_FILE):
    if not vocab_list:
        return
    fieldnames = ['word', 'meaning', 'phonetic', 'language', 'review_count', 'last_review', 'is_mastered', 'last_result', 'example', 'type', 'category', 'level']
    existing_data = []
    if os.path.exists(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)
    updated_dict = {row['word']: row for row in vocab_list}
    for row in existing_data:
        if row['word'] in updated_dict:
            row.update(updated_dict[row['word']])
        else:
            updated_dict[row['word']] = row
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in updated_dict.values():
            writer.writerow({k: v for k, v in row.items() if k in fieldnames})

# === FUNCTION: So sánh ngôn ngữ linh hoạt ===
def is_similar(answer, correct_answer):
    answer = answer.strip().lower()
    correct_answer = correct_answer.strip().lower()
    if answer == correct_answer:
        return True
    if answer in correct_answer or correct_answer in answer:
        return True
    similarity = difflib.SequenceMatcher(None, answer, correct_answer).ratio()
    return similarity >= 0.9

# === FUNCTION: Thống kê top 5 sai gần nhất ===
def show_recent_wrong_words(file_path=CSV_FILE):
    if not os.path.exists(file_path):
        return
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        wrong_words = [row for row in reader if row.get('last_result') == 'wrong']
        wrong_words = sorted(wrong_words, key=lambda x: x['last_review'], reverse=True)
        print("\n📉 Top 5 từ sai gần đây:")
        for i, row in enumerate(wrong_words[:5], 1):
            print(f"{i}. {row['word']} ({row['phonetic']}) - {row['meaning']} - ôn gần nhất: {row['last_review']}")

# === FUNCTION: Review flashcards ===
def review_session(lang, user_level):
    words = get_words_to_review(language_filter=lang, user_level=user_level)
    if not words:
        print("\n⚠️ Không có từ nào phù hợp để ôn tập.")
        return

    print("\n📚 Bắt đầu ôn tập:")
    for word in words:
        print(f"\nTừ: {word['word']}")
        print(f"Phiên âm: {word['phonetic']}")
        print(f"Ví dụ: {word.get('example', 'Không có ví dụ.')}")
        answer = input("Nhập nghĩa tiếng Việt của từ này: ").strip().lower()
        correct_answer = word['meaning'].strip().lower()
        correct = is_similar(answer, correct_answer)
        if correct:
            print("✅ Chính xác!")
        else:
            print(f"❌ Sai. Nghĩa đúng là: {word['meaning']}")
            log_history("wrong", word['word'], word.get('category', ''), lang)

        word.update(update_word(word, correct))
        print("-" * 30)

    save_vocab_list(words)
    print("\n✅ Đã cập nhật trạng thái ôn tập.")
    show_recent_wrong_words()

    # ==== Kiểm tra tỷ lệ đúng và gợi ý nâng cấp độ ====
    correct_words = [w for w in words if w.get('last_result') == 'correct']
    total_words = len(words)
    correct_ratio = len(correct_words) / total_words if total_words else 0

    if user_level < 5:
        next_level = user_level + 1

        if correct_ratio == 1.0:
            print(f"🎉 Chúc mừng 🏆 Bạn đã học thuộc 100% từ vựng cấp độ {user_level}. Bạn sẽ được chuyển lên cấp {next_level}!")
            config = load_config()
            config['user_level'] = next_level
            save_config(config)
        elif correct_ratio >= 0.9:
            print(f"🎉 Bạn đã học thuộc {round(correct_ratio * 100)}% từ cấp độ {user_level}!")
            choice = input("👉 Bạn có muốn chuyển lên cấp độ tiếp theo không? (y/n): ").strip().lower()
            if choice == 'y':
                config = load_config()
                config['user_level'] = next_level
                save_config(config)
                print(f"🚀 Tuyệt vời! Bạn đã được chuyển lên cấp {next_level}.")
            else:
                print("👍 Tuyệt vời, bạn có thể tiếp tục ôn luyện để nắm chắc hơn cấp hiện tại.")
        elif correct_ratio >= 0.8:
            print(f"👏 Bạn đã nhớ {round(correct_ratio * 100)}% từ cấp độ {user_level}!")
            choice = input("👉 Bạn có muốn chuyển lên cấp độ tiếp theo không? (y/n): ").strip().lower()
            if choice == 'y':
                config = load_config()
                config['user_level'] = next_level
                save_config(config)
                print(f"🚀 Tuyệt vời! Bạn đã được chuyển lên cấp {next_level}.")
            else:
                print("👍 Bạn có thể tiếp tục ôn tập thêm để tự tin hơn.")
        elif correct_ratio >= 0.7:
            print(f"🙂 Bạn đã học được {round(correct_ratio * 100)}% từ vựng cấp độ {user_level}.")
            choice = input("👉 Bạn có muốn chuyển lên cấp độ tiếp theo không? (y/n): ").strip().lower()
            if choice == 'y':
                config = load_config()
                config['user_level'] = next_level
                save_config(config)
                print(f"🚀 Rất tốt! Bạn đã được chuyển lên cấp {next_level}.")
            else:
                print("👍 Tuyệt vời, bạn có thể tiếp tục ôn luyện để nắm chắc hơn cấp hiện tại.")

# === FUNCTION: Learn new words ===
def learn_new_words(lang, user_level, goal=5):
    if not os.path.exists(CSV_FILE):
        print("⚠️ Không tìm thấy dữ liệu.")
        return

    # Lấy các category học nhiều nhất để ưu tiên
    top_categories = get_top_categories_from_history(top_n=3)
    category_priority = {cat: 3 - idx for idx, (cat, _) in enumerate(top_categories)}

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        new_words = []

        for row in reader:
            if row.get('review_count', '0') == '0' and row.get('language', '') == lang:
                raw_level = row.get('level', '').strip()
                category = row.get('category', '')
                if raw_level.isdigit():
                    level = int(raw_level)
                    if level <= user_level:
                        # Gán điểm ưu tiên theo chủ đề
                        row['priority'] = category_priority.get(category, 0)
                        new_words.append(row)

    # Sắp xếp từ mới theo độ ưu tiên giảm dần
    new_words.sort(key=lambda x: -x['priority'])

    if not new_words:
        print(f"🎉 Bạn đã học hết từ mới rồi!")
        return

    print(f"\n📘 Học {min(goal, len(new_words))} từ mới tiếng {lang} hôm nay:\n")
    today = datetime.today().strftime("%Y-%m-%d")
    learned = []

    for word in new_words[:goal]:
        print(f"Từ: {word['word']}")
        print(f"Phiên âm: {word.get('phonetic', 'Không có')}")
        print(f"Nghĩa: {word.get('meaning', 'Không rõ nghĩa')}")
        print(f"Ví dụ: {word.get('example', 'Không có ví dụ.')}")
        mark = input("→ Đánh dấu từ này là đã học? (y/n): ").strip().lower()
        if mark == 'y':
            word['review_count'] = '1'
            word['last_review'] = today
            word['last_result'] = 'correct'
            word['is_mastered'] = 'False'
            learned.append(word)
            log_history("learn", word['word'], word.get('category', ''), lang)

            # 🧠 Nếu người học đang ở cấp độ 2: kiểm tra ngữ pháp đơn giản
           
        print("-" * 30)

    if learned:
        save_vocab_list(learned)
        print(f"\n✅ Đã cập nhật {len(learned)} từ đã học.")
    else:
        print("👍 Không có từ nào được đánh dấu là đã học.")

# === FUNCTION: Tra cứu từ ===
def lookup_word(lang):
    keyword = input("\n🔍 Nhập từ bạn muốn tra cứu: ").strip().lower()
    found = False

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['word'].strip().lower() == keyword and row['language'] == lang:
                print(f"\n📖 Kết quả tra cứu:")
                print(f"Từ: {row['word']}")
                print(f"Phiên âm: {row.get('phonetic', '')}")
                print(f"Nghĩa: {row.get('meaning', '')}")
                print(f"Ví dụ: {row.get('example', '')}")
                print(f"Loại từ: {row.get('type', '')}")
                print(f"Chủ đề: {row.get('category', '')}")
                print(f"Cấp độ: {row.get('level', '')}")
                found = True
                log_history("lookup", row['word'], row['category'], lang)
                break

    if not found:
        print("❌ Từ này chưa có trong dữ liệu.")
        choice = input("👉 Bạn có muốn thêm từ này không? (y/n): ").strip().lower()
        if choice == 'y':
            add_new_word_with_check()
# === FUNCTION: Menu học từ mới (tra từ hoặc học 5 từ/ngày) ===
def learn_new_word_menu(lang, user_level):
    print("\n1. 🔍 Tra từ ")
    print("2. 📘 Học 5 từ mới mỗi ngày")
    choice = input("Chọn chức năng học từ mới (1 hoặc 2): ").strip()

    if choice == '1':
        lookup_word(lang)
    elif choice == '2':
        learn_new_words(lang, user_level)
    else:
        print("❌ Lựa chọn không hợp lệ.")
# === FUNCTION: phân tích hành vi ===
from collections import Counter

def get_top_categories_from_history(top_n=3):
    if not os.path.exists("history.csv"):
        return []

    with open("history.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        categories = [row['category'] for row in reader if row.get('category')]
        counter = Counter(categories)
        return counter.most_common(top_n)
# === FUNCTION: tạo báo cáo học tập ===
def generate_learning_report():
    if not os.path.exists("history.csv"):
        print("⚠️ Chưa có dữ liệu hành vi để tạo báo cáo.")
        return

    from collections import Counter
    import csv

    total_actions = 0
    learn_count = 0
    correct_count = 0
    wrong_count = 0
    lookup_count = 0

    category_counter = Counter()
    wrong_category_counter = Counter()
    language_counter = Counter()

    with open("history.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            action = row['action']
            category = row.get('category', '')
            lang = row.get('language', '')

            total_actions += 1
            language_counter[lang] += 1

            if action == "learn":
                learn_count += 1
                category_counter[category] += 1
            elif action == "wrong":
                wrong_count += 1
                wrong_category_counter[category] += 1
            elif action == "correct":
                correct_count += 1
            elif action == "lookup":
                lookup_count += 1

    print("\n📊 BÁO CÁO HỌC TẬP TỪ history.csv")
    print(f"- Tổng số lượt học: {learn_count}")
    print(f"- Tổng số lượt tra từ: {lookup_count}")
    print(f"- Tổng số câu đúng: {correct_count}")
    print(f"- Tổng số câu sai: {wrong_count}")

    total_answered = correct_count + wrong_count
    if total_answered > 0:
        accuracy = round(correct_count / total_answered * 100, 2)
        print(f"- Tỉ lệ trả lời đúng: {accuracy}%")
    else:
        print("- Chưa có dữ liệu đúng/sai.")

    if category_counter:
        top_cat = category_counter.most_common(1)[0]
        print(f"- Chủ đề học nhiều nhất: {top_cat[0]} ({top_cat[1]} lần)")

    if wrong_category_counter:
        top_wrong = wrong_category_counter.most_common(1)[0]
        print(f"- Chủ đề sai nhiều nhất: {top_wrong[0]} ({top_wrong[1]} sai)")

    if language_counter:
        top_lang = language_counter.most_common(1)[0]
        print(f"- Ngôn ngữ học chính: {top_lang[0]}")
# === MINI GAME SESSION: Mixed Unlimited Play ===
def play_game_session(lang, user_level):
    if not os.path.exists(CSV_FILE):
        print("⚠️ Không tìm thấy dữ liệu từ vựng.")
        return

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        vocab = [
            row for row in reader
            if int(row['review_count']) >= 1
            and row['language'] == lang
            and int(row.get('level', '5')) <= user_level
        ]

    if len(vocab) < 10:
        print("⚠️ Bạn cần ít nhất 10 từ đã học để chơi game.")
        return

    score = 0
    total = 0
    mistakes = 0
    max_mistakes = 3

    print("\n🎮 BẮT ĐẦU PHIÊN CHƠI MINI-GAME!")
    print("(Nhấn 'q' bất kỳ lúc nào để thoát.)\n")

    while True:
        user_input = input("👉 Nhấn Enter để chơi tiếp, hoặc 'q' để thoát: ").strip().lower()
        if user_input == 'q':
            break

        game_type = random.choice(['match', 'type', 'odd'])

        if game_type == 'match':
            correct = play_game_match(vocab)
        elif game_type == 'type':
            correct = play_game_type(vocab)
        else:
            correct = play_game_odd_one_out(vocab)

        total += 1
        if correct:
            score += 1
        else:
            mistakes += 1
            if mistakes >= max_mistakes:
                print(f"\n❌ Bạn đã trả lời sai quá {max_mistakes} câu. Mini game kết thúc!")
                break

    print("\n📊 KẾT QUẢ PHIÊN CHƠI:")
    print(f"Số câu đúng: {score}/{total}")
    if total > 0:
        print(f"Tỷ lệ đúng: {round(score / total * 100, 2)}%")
    print("👍 Cảm ơn bạn đã tham gia!")
def play_game_match(vocab):
    if len(vocab) < 4:
        print("⚠️ Cần ít nhất 4 từ vựng để chơi trò chơi.")
        return False

    word = random.choice(vocab)
    correct_answer = word['meaning']
    options = [correct_answer]

    meanings = list(set([w['meaning'] for w in vocab if w['meaning'] != correct_answer]))
    random.shuffle(meanings)
    options += meanings[:3]
    random.shuffle(options)

    print(f"\n🔤 Từ: {word['word']}")
    print("Nghĩa nào là đúng?")
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt}")

    answer = input("Chọn đáp án (1–4) hoặc gõ nghĩa: ").strip().lower()

    # Kiểm tra nếu là số từ 1–4
    if answer in ['1', '2', '3', '4']:
        chosen = options[int(answer) - 1]
    else:
        # Tìm trong danh sách các đáp án xem người dùng gõ giống cái nào
        matched = [opt for opt in options if opt.lower() == answer]
        if not matched:
            print("❌ Không nhận diện được đáp án.")
            print(f"📘 Đáp án đúng là: {correct_answer}")
            return False
        chosen = matched[0]

    if chosen == correct_answer:
        print("✅ Chính xác!")
    else:
        print("❌ Sai.")
    print(f"📘 Đáp án đúng là: {correct_answer}")
    return chosen == correct_answer
# === MINI GAME: Type English Word from Meaning ===
def play_game_type(vocab):
    word = random.choice(vocab)
    correct_word = word['word'].strip().lower()

    print(f"\n📝 Nghĩa tiếng Việt: {word['meaning']}")
    answer = input("Từ tiếng Anh là gì? ").strip().lower()

    if answer == correct_word:
        print("✅ Chính xác!")
        return True
    else:
        print(f"❌ Sai. Đáp án đúng là: {word['word']}")
        return False
def play_game_odd_one_out(vocab):
    filtered_vocab = [word for word in vocab if word.get('category') and word.get('type')]
    if len(filtered_vocab) < 4:
        print("⚠️ Không đủ dữ liệu để tạo câu hỏi.")
        return False

    grouping_field = random.choice(['type', 'category'])
    group_candidates = [word[grouping_field] for word in filtered_vocab]
    selected_group = random.choice(list(set(group_candidates)))
    same_group_words = [w for w in filtered_vocab if w[grouping_field] == selected_group]

    if len(same_group_words) < 3:
        return False

    wrong_word = random.choice([w for w in filtered_vocab if w[grouping_field] != selected_group])
    options = random.sample(same_group_words, 3) + [wrong_word]
    random.shuffle(options)

    print("\n🧠 Chọn từ KHÁC NHÓM so với 3 từ còn lại:")
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt['word']}")

    answer = input("Chọn số thứ tự từ khác nhóm (1–4): ").strip()
    if answer not in ['1', '2', '3', '4']:
        print("❌ Lựa chọn không hợp lệ.")
        return False

    chosen = options[int(answer)-1]
    if chosen[grouping_field] != selected_group:
        print("✅ Chính xác!")
        return True
    else:
        print(f"❌ Sai. Từ đúng là: {wrong_word['word']} ({wrong_word['meaning']})")
        print(f"🧠 Ba từ còn lại thuộc nhóm '{grouping_field}': '{selected_group}'")
        return False

# === MAIN MENU ===
def main():
    config = load_config()

    # Nếu chưa có ngôn ngữ/cấp độ, hỏi người dùng
    if not config.get("language") or not config.get("user_level"):
        print("\n🌐 Chọn ngôn ngữ bạn muốn học:")
        print("1. English")
        print("2. Korean")
        lang_choice = input("Chọn 1 hoặc 2: ").strip()
        config['language'] = 'English' if lang_choice != '2' else 'Korean'

        print("\n🎯 Chọn cấp độ học của bạn:")
        print("1. Starter")
        print("2. Beginner")
        print("3. Pre-Intermediate")
        print("4. Intermediate")
        print("5. Advanced")
        config['user_level'] = int(input("Nhập số cấp độ (1–5): ").strip())

        save_config(config)

    lang = config['language']
    user_level = config['user_level']
    level_names = {
    1: "Starter",
    2: "Beginner",
    3: "Pre-Intermediate",
    4: "Intermediate",
    5: "Advanced"
    }
    current_level_name = level_names.get(user_level, "Unknown")
    next_level_name = level_names.get(user_level + 1, "Advanced")

    print(f"\n🎯 Bạn đang ở cấp độ {user_level} – {current_level_name}.")
    if user_level < 5:
        print(f"👉 Hãy duy trì học 5 từ mới mỗi ngày để lên cấp độ {user_level + 1} – {next_level_name}!")
    else:
        print("🎓 Bạn đã đạt cấp độ cao nhất! Hãy tiếp tục ôn tập để giữ vững kiến thức.")
    while True:
        print("\n--- AI Vocabulary Coach ---")
        print("1. Học từ mới")
        print("2. Ôn tập từ vựng")
        print("3. Thêm từ mới")
        print("4. Chơi mini game")
        print("5. Đổi ngôn ngữ / cấp độ")
        print("6. Xem báo cáo học tập")
        print("7. Thoát")
        choice = input("Chọn một mục (1/2/3/4/5/6/7): ").strip()

        if choice == '1':
            learn_new_word_menu(lang, user_level)
        elif choice == '2':
            review_session(lang, user_level)
        elif choice == '3':
            add_new_word_with_check()
        elif choice == '4':
            play_game_session(lang, user_level)
        elif choice == '5':
            print("\n🌐 Chọn ngôn ngữ bạn muốn học:")
            print("1. English")
            print("2. Korean")
            lang_choice = input("Chọn 1 hoặc 2: ").strip()
            config['language'] = 'English' if lang_choice != '2' else 'Korean'

            print("\n🎯 Chọn cấp độ học của bạn:")
            print("1. Starter")
            print("2. Beginner")
            print("3. Pre-Intermediate")
            print("4. Intermediate")
            print("5. Advanced")
            config['user_level'] = int(input("Nhập số cấp độ (1–5): ").strip())

            save_config(config)
            lang = config['language']
            user_level = config['user_level']
            print("✅ Đã cập nhật ngôn ngữ và cấp độ.")
        elif choice == '6':
            generate_learning_report()
        elif choice == '7':
            print("Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ.Vui lòng chọn số từ 1 đến 6.")

if __name__ == '__main__':
    main()