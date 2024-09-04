try:
        combined_text = ''.join(text)  # Combine individual characters into a single string
        translated_text = translator.translate(combined_text, dest=selected_language).text

    except ValueError as e:
        return f"Error: {e}"