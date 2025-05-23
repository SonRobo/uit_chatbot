"""
This module is used for preprocessing queries
"""

import re
from difflib import SequenceMatcher
from typing import Any
from underthesea import word_tokenize
import torch
import numpy as np

from src.models.preprocess import ProcessedData
from src.prompt.postprocessing_prompt import (
    RESPONSE_UNSUPPORTED_LANGUAGE,
    RESPONSE_PROMPT_INJECTION
)
from src.prompt.preprocessing_prompt import (
    FILLTER_WORDS,
    TERMS_DICT,
    SHORT_CHAT,
    RESPONSE_DICT,
    TOKENIZER_WORD_PREFIX,
    PROMPT_INJECTION_PATTERNS,
    POTENTIAL_PROMPT_INJECTION_PATTERNS
)


class PreprocessQuestion:
    """
    Handles the preprocessing of queries.
    """

    def __init__(
        self,
        domain_clf_model,
        lang_detect_model,
        tonemark_model,
        tonemark_tokenizer,
        prompt_injection_model,
        device_type,
        label_list
    ) -> None:
        """
        Initializes the model manager with various models and vectorizers.

        Args:
            domain_clf_model: The model used for domain classification.
            domain_clf_vectorizer: The vectorizer associated with the domain classification model.
            lang_detect_model: The model used for language detection.
            tonemark_model: The model used for tonemark prediction.
            tonemark_tokenizer: The tokenizer associated with the tonemark model.
            prompt_injection_model: The model used for detecting prompt injection.
            prompt_injection_vectorizer: The vectorizer associated with the prompt injection model.
            device_type: The type of device (e.g., 'cpu', 'cuda') used for model inference.
            label_list: A list of labels used in classification tasks.

        Returns:
            None
        """
        self.domain_clf_model = domain_clf_model
        self.lang_detect_model = lang_detect_model
        self.tonemark_model = tonemark_model
        self.tonemark_tokenizer = tonemark_tokenizer
        self.prompt_injection_model = prompt_injection_model
        self.device_type = device_type
        self.label_list = label_list

    # @staticmethod
    # def normalize_elonge_word(text):
    #     """
    #     Normalizes elongated words in a given text by removing consecutive duplicate characters.

    #     Args:
    #         text (str): The input text containing potentially elongated words.

    #     Returns:
    #         str: A normalized version of the text with elongated words shortened by removing
    #             consecutive duplicate characters.
    #     """
    #     s_new = ''
    #     for word in text.split(' '):
    #         word_new = ' '
    #         for char in word.strip():
    #             if char != word_new[-1]:
    #                 word_new += char
    #         s_new += word_new.strip() + ' '
    #     return s_new.strip()

    @staticmethod
    def normalize_elonge_word(text):
        """
        Normalizes elongated words in a given text by removing consecutive duplicate characters,
        while preserving numeric characters and punctuation.

        Args:
            text (str): The input text containing potentially elongated words.

        Returns:
            str: A normalized version of the text with elongated words shortened by removing
                consecutive duplicate characters, while preserving all numeric characters.
        """
        s_new = []

        for word in text.split(' '):
            word_new = ''
            prev_char = ''
            for char in word:
                if char.isdigit() or char != prev_char:
                    word_new += char
                    prev_char = char
            s_new.append(word_new)

        return ' '.join(s_new)

    @staticmethod
    def replace_symbols(text) -> str:
        """
        Replaces specific symbols in the input text.

        Args:
            text (str): The input text containing symbols to be replaced.

        Returns:
            str: A text with specific symbols replaced by their corresponding descriptions
                or removed, with extra spaces cleaned up.
        """
        replacements = {
            ">": " lớn hơn ",
            "<": " bé hơn ",
            "=": " bằng ",
            "$": " ",
            "#": " ",
            "^": " ",
            "/": " ",
            "!": " "
        }

        for symbol, replacement in replacements.items():
            text = text.replace(symbol, replacement)

        return " ".join(text.split())

    @staticmethod
    def replace_synonyms(
        text,
        synonym_dict: Any
    ) -> str:
        """
        Replaces synonyms in the input text

        Args:
            text (str): The input text in which synonyms need to be replaced.
            synonym_dict (dict): A dictionary where keys are target keywords and values.

        Returns:
            str: The text with synonyms replaced by their corresponding keywords.
        """
        text = text.lower()

        for keyword, synonyms in synonym_dict.items():
            keyword = keyword.lower()
            for synonym in synonyms:
                synonym = synonym.strip().lower()
                text = re.sub(r'\b{}\b'.format(
                    re.escape(synonym)), keyword, text)

        return text

    @staticmethod
    def remove_emojis(text):
        """
        Removes all emojis from the input text.

        Args:
            text (str): The input text from which emojis need to be removed.

        Returns:
            str: The text with all emojis removed.
        """
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    @staticmethod
    def remove_filler_words(
        text: str,
        filler_words: Any
    ):
        """
        Removes specified filler words from the input text.

        Args:
            text (str): The input text from which filler words need to be removed.
            filler_words (list): A list of filler words (e.g., "uh", "um").

        Returns:
            str: The text with the specified filler words removed and extra spaces cleaned up.
        """
        text = text.lower()

        for word in filler_words:
            pattern = r'\b{}\b'.format(
                re.escape(word.strip().lower())
            )
            text = re.sub(pattern, '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def delete_non_vietnamese_characters(text):
        """
        Removes characters from the input text that are not part of the Vietnamese alphabet,
        including numbers, Vietnamese diacritics, and certain punctuation marks.

        Args:
            text (str): The input text from which non-Vietnamese characters need to be removed.

        Returns:
            str: The text with non-Vietnamese characters removed.
        """
        pattern = r"[0-9a-zA-ZaăâbcdđeêghiklmnoôơpqrstuưvxyàằầbcdđèềghìklmnòồờpqrstùừvxỳáắấbcdđéếghíklmnóốớpqrstúứvxýảẳẩbcdđẻểghỉklmnỏổởpqrstủửvxỷạặậbcdđẹệghịklmnọộợpqrstụựvxỵãẵẫbcdđẽễghĩklmnõỗỡpqrstũữvxỹAĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXYÀẰẦBCDĐÈỀGHÌKLMNÒỒỜPQRSTÙỪVXỲÁẮẤBCDĐÉẾGHÍKLMNÓỐỚPQRSTÚỨVXÝẠẶẬBCDĐẸỆGHỊKLMNỌỘỢPQRSTỤỰVXỴẢẲẨBCDĐẺỂGHỈKLMNỎỔỞPQRSTỦỬVXỶÃẴẪBCDĐẼỄGHĨKLMNÕỖỠPQRSTŨỮVXỸ,._]"

        return re.sub(rf'[^{pattern}\s]', '', text).strip()

    @staticmethod
    def merge_tokens_and_preds(
        tokens,
        predictions
    ):
        """
        Merges tokens and their predictions, combining split tokens and their labels.

        Args:
            tokens (list of str): Tokenized text.
            predictions (list of int/str): Prediction labels for each token.

        Returns:
            list of tuples: Merged tokens with corresponding sets of labels.
        """
        merged_tokens_preds = []
        i = 0

        while i < len(tokens):
            tok = tokens[i]
            label_indexes = set([predictions[i]])

            if tok.startswith(TOKENIZER_WORD_PREFIX):
                tok_no_prefix = tok[len(TOKENIZER_WORD_PREFIX):]
                cur_word_toks = [tok_no_prefix]
                j = i + 1

                while j < len(tokens):
                    if not tokens[j].startswith(TOKENIZER_WORD_PREFIX):
                        cur_word_toks.append(tokens[j])
                        label_indexes.add(predictions[j])
                        j += 1
                    else:
                        break

                cur_word = ''.join(cur_word_toks)
                merged_tokens_preds.append((cur_word, label_indexes))
                i = j

            else:
                merged_tokens_preds.append((tok, label_indexes))
                i += 1

        return merged_tokens_preds

    @staticmethod
    def get_accented_words(
        merged_tokens_preds,
        label_list
    ):
        """
        Adds accents to words based on prediction labels.

        Args:
            merged_tokens_preds (list of tuples): Merged tokens with label indexes.
            label_list (list of str): Labels indicating accent mappings.

        Returns:
            list of str: Words with applied accents.
        """
        accented_words = []

        for word_raw, label_indexes in merged_tokens_preds:
            for label_index in label_indexes:
                tag_name = label_list[int(label_index)]
                raw, vowel = tag_name.split("-")
                if raw and raw in word_raw:
                    word_accented = word_raw.replace(raw, vowel)
                    break
            else:
                word_accented = word_raw
            accented_words.append(word_accented)

        return accented_words

    def is_prompt_injection(
        self,
        text
    ):
        """
        Checks if the text contains patterns indicative of prompt injection.

        Args:
            text (str): The input text to be checked.

        Returns:
            bool: True if prompt injection patterns are detected; False otherwise.
        """
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        for pattern in POTENTIAL_PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if self.prompt_injection_model.predict_proba(
                    [text]
                )[0][0] >= 0.5:
                    return True

        return False

    def detect_short_chat(
        self,
        text_input
    ):
        """
        Detects if the input text is a short chat message based on patterns and emojis.

        Args:
            text_input (str): The input text to be analyzed.

        Returns:
            bool: True if the text is detected as a short chat message; False otherwise.
        """
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        normalized_text = text_input.lower().strip()
        has_emoji = bool(emoji_pattern.search(normalized_text))

        def is_similar(text1, text2, threshold=0.85):
            return SequenceMatcher(None, text1, text2).ratio() >= threshold
        matches_pattern = any(is_similar(normalized_text, pattern)
                              for pattern in SHORT_CHAT)
        if has_emoji:
            if matches_pattern or normalized_text == '':
                return True
        elif matches_pattern:
            return True

        return False

    def insert_accents(
        self,
        text,
        model,
        tokenizer
    ):
        """
        Inserts accents into the text using a model and tokenizer.

        Args:
            text (str): The input text to process.
            model: The model used for accent prediction.
            tokenizer: The tokenizer to process and convert tokens.

        Returns:
            tuple: A tuple containing the list of tokens and their predicted accents.
        """
        our_tokens = text.strip().split()
        inputs = tokenizer(our_tokens,
                           is_split_into_words=True,
                           truncation=True,
                           padding=True,
                           return_tensors="pt"
                           )
        input_ids = inputs['input_ids']
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
        tokens = tokens[1:-1]

        with torch.no_grad():
            inputs.to(self.device_type)
            outputs = model(**inputs)

        predictions = outputs["logits"].cpu().numpy()
        predictions = np.argmax(predictions, axis=2)
        predictions = predictions[0][1:-1]
        assert len(tokens) == len(predictions)

        return tokens, predictions

    def get_response(
        self,
        input_text,
        short_chats,
        response_dict,
        threshold=0.9
    ):
        """
        Finds the best matching short chat and returns the corresponding response.

        Args:
            input_text (str): The input text to match.
            short_chats (list of str): List of short chat patterns to match against.
            response_dict (dict): Dictionary mapping short chats to responses.
            threshold (float, optional): Similarity ratio threshold for matching. Default is 0.9.

        Returns:
            str: The response corresponding to the best match or a default message.
        """
        input_text = input_text.lower().strip()
        best_match = None
        best_ratio = 0.0

        for chat in short_chats:
            ratio = SequenceMatcher(None, input_text, chat).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = chat

        if best_match and best_match in response_dict:
            return response_dict[best_match]

        return "Mình chưa hiểu rõ ý bạn lắm."

    def clean_text(
        self,
        text,
        term_dict
    ):
        """
        Cleans and normalizes the input text using various text processing methods.

        Args:
            text (str): The input text to clean.
            term_dict (dict): Dictionary for replacing synonyms.

        Returns:
            str: The cleaned and normalized text.
        """
        text = re.sub(r'\s+', ' ', text)
        text = self.delete_non_vietnamese_characters(text.lower())
        text = self.remove_filler_words(text, FILLTER_WORDS)
        text = self.remove_emojis(text)
        text = self.replace_synonyms(text, term_dict)
        text = self.replace_symbols(text)
        text = self.normalize_elonge_word(text)

        return text

    def lang_detect_2(
        self,
        text: str = None
    ):
        """
        Detects the language of the input text and returns the most likely language and its score.

        Args:
            text (str): The input text for language detection.

        Returns:
            tuple: A tuple containing the most likely language and its detection score. 
                Returns (None, 0) if no language is detected.
        """
        prediction = self.lang_detect_model.predict(text)
        lang_scores = {label.replace('__label__', ''): score for label, score in zip(
            prediction[0], prediction[1]
        )}

        if lang_scores:
            most_likely_lang = max(lang_scores, key=lang_scores.get)
            highest_score = lang_scores[most_likely_lang]
        else:
            most_likely_lang = None
            highest_score = 0

        return most_likely_lang, highest_score

    # def correct_vietnamese_text(
    #     self,
    #     text
    # ):
    #     """
    #     Corrects the accents in Vietnamese text using a model and tokenizer.

    #     Args:
    #         text (str): The input Vietnamese text to correct.

    #     Returns:
    #         str: The Vietnamese text with corrected accents.
    #     """
    #     tokens, predictions = self.insert_accents(
    #         text,
    #         self.tonemark_model,
    #         self.tonemark_tokenizer
    #     )
    #     merged_tokens_preds = self.merge_tokens_and_preds(tokens, predictions)
    #     accented_words = self.get_accented_words(
    #         merged_tokens_preds,
    #         self.label_list
    #     )

    #     return ' '.join(accented_words)

    def tokenize_text(
        self,
        text
    ):
        """
        Tokenizes the input text into a list of words.

        Args:
            text (str): The input text to tokenize.

        Returns:
            list of str: A list of tokens (words) from the input text.
        """
        tokens = word_tokenize(text, format='text')

        return tokens

    def classify_domain(
        self,
        text
    ):
        """
        Classifies the domain of the input text using a pre-trained model.

        Args:
            text (str): The input text to classify.

        Returns:
            str: The predicted domain for the input text.
        """
        # Preprocess the text
        if len(text) <= 30:
            return 0

        processed_text = self.tokenize_text(text)
        score_prediction = self.domain_clf_model.predict_proba(
            [processed_text]
        )[0][1]
        print(f"score domain: {score_prediction}")

        if score_prediction >= 0.6:
            return 1

        return 0

    async def detect_icon(
        self,
        text: str
    ) -> bool:
        """
        Detects if the given text contains an emoji or an emoticon.

        Args:
            text (str): The text to be checked for emojis or emoticons.

        Returns:
            bool: True if the text contains an emoji or emoticon; otherwise, False.
        """
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        emoticon_pattern = re.compile(r"(:|=|;)(\)+|\(+|D+|P+)")

        return bool(emoji_pattern.fullmatch(
            text) or emoticon_pattern.fullmatch(text))

    async def preprocess_text(
        self,
        text_input
    ):
        """
        Preprocesses the input text to classify it and detect various conditions
        such as short chat, language, and prompt injection.

        Args:
            text_input (str): The input text to preprocess.

        Returns:
            Union[ShortChat, UnsupportedLanguage, PromptInjection, ProcessedData]: 
                - ShortChat if the text is detected as a short chat.
                - UnsupportedLanguage if the detected language is not supported.
                - PromptInjection if prompt injection is detected.
                - ProcessedData with various flags and processed text otherwise.
        """
        query = ""
        language = True
        prompt_injection = False
        outdomain = False
        short_chat = False

        if await self.detect_icon(text_input):
            return ProcessedData(
                query=text_input,
                language=True,
                is_prompt_injection=False,
                is_outdomain=False,
                is_short_chat=False,
                is_only_icon=True
            )

        clean_text_input = self.clean_text(text_input, TERMS_DICT)
        is_short_chat = self.detect_short_chat(clean_text_input)

        if is_short_chat:
            query = self.get_response(
                clean_text_input,
                SHORT_CHAT,
                RESPONSE_DICT,
                threshold=0.9
            )
            return ProcessedData(
                query=query,
                language=language,
                is_prompt_injection=prompt_injection,
                is_outdomain=outdomain,
                is_short_chat=is_short_chat,
                is_only_icon=False
            )

        if short_chat is False:
            lang, _ = self.lang_detect_2(clean_text_input)
            corrected_text = clean_text_input
            if lang != "vie_Latn":
                language = False
                return ProcessedData(
                    query=RESPONSE_UNSUPPORTED_LANGUAGE,
                    language=language,
                    is_prompt_injection=prompt_injection,
                    is_outdomain=outdomain,
                    is_short_chat=short_chat,
                    is_only_icon=False
                )

            if language:
                if self.is_prompt_injection(corrected_text):
                    prompt_injection = True
                    return ProcessedData(
                        query=RESPONSE_PROMPT_INJECTION,
                        language=language,
                        is_prompt_injection=prompt_injection,
                        is_outdomain=outdomain,
                        is_short_chat=short_chat,
                        is_only_icon=False
                    )
                domain = self.classify_domain(corrected_text)
                if domain == 1:
                    outdomain = True
                if language and not outdomain:
                    query = corrected_text
                else:
                    query = corrected_text
            else:
                query = text_input

        return ProcessedData(
            query=query,
            language=language,
            is_prompt_injection=prompt_injection,
            is_outdomain=outdomain,
            is_short_chat=short_chat,
            is_only_icon=False
        )
