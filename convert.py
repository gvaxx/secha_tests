import fitz  # PyMuPDF
import re
import json
# Финальный и наиболее надежный парсер с окончательной очисткой
def fully_correct_parse(text):
    pattern = r'(ЗС|ПБ|ИСМП|ДС|АИ|ИПКП|ИПОВ|ИППП|ИПЭП|КИ|ОЭ|УЭП|ЭНИБ)\s?\d{1,3}'
    splits = re.split(f'(?={pattern})', text)
    questions = []

    for block in splits[1:]:
        lines = block.strip().split("\n")
        qid_match = re.match(pattern, lines[0])
        if not qid_match:
            continue

        qid = qid_match.group(0).replace(' ', '')
        lines = lines[1:]

        question, options, answers = [], [], []
        mode = "question"
        
        for line in lines:
            line = line.strip()
            if re.match(r'^[а-яa-z]\)', line, re.IGNORECASE):
                mode = "options"
                options.append(line)
            elif re.fullmatch(r'(?:[А-ЯЁ]\s*)+', line.strip()):
                mode = "answers"
                answers.extend(line.strip().split())
            else:
                if mode == "question":
                    question.append(line)
                elif mode == "options" and options:
                    options[-1] += " " + line

        # Очистка ответов от случайных букв (оставляем только уникальные буквы опций)
        option_letters = set(opt[0].upper() for opt in options if re.match(r'^[а-яa-z]\)', opt, re.IGNORECASE))
        correct_answers = [ans for ans in answers if ans in option_letters]

        # Перенос лишних букв обратно в вопрос
        wrong_answers = [ans for ans in answers if ans not in option_letters]
        question_text = " ".join(question + wrong_answers).replace("  ", " ").strip()

        # Удаление повторов букв ответов
        correct_answers = sorted(list(set(correct_answers)))

        questions.append({
            "id": qid,
            "question": question_text,
            "options": options,
            "answers": correct_answers
        })

    return questions

# Финальный запуск
final_questions_fully_corrected = fully_correct_parse()

# Сохраняем окончательный чистый JSON
final_json_clean_path = "parsed_questions.json"
with open(final_json_clean_path, "w", encoding="utf-8") as f:
    json.dump(final_questions_fully_corrected, f, ensure_ascii=False, indent=2)


