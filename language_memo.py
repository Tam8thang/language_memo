import FreeSimpleGUI as sg
import sqlite3
from contextlib import contextmanager

#Test Comment

try:
    linux_font = 'DejaVu Sans'
    # Test if font exists by creating a temporary Text element
    #sg.Text('test', font=(linux_font, 11)).get_size()
except:
    linux_font = 'Sans'  # Fallback to default system font

def get_location(window):
    x, y = window.current_location()
    w, h = window.size
    popup_w, popup_h = 200, 60  # Approximate popup size
    popup_x = x + (w - popup_w) // 2
    popup_y = y + (h - popup_h) // 2
    return (popup_x, popup_y)

# Database setup
def initialize_database():
    with sqlite3.connect('language_pairs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS languages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language_name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english_sentence TEXT NOT NULL,
                foreign_sentence TEXT NOT NULL,
                language_id INTEGER NOT NULL,
                FOREIGN KEY (language_id) REFERENCES languages (id)
            )
        ''')
        conn.commit()

# Database helper functions
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('language_pairs.db')
    try:
        yield conn
    finally:
        conn.close()

def fetch_languages():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT language_name FROM languages')
        return [row[0] for row in cursor.fetchall()]

def add_language(language_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO languages (language_name) VALUES (?)', (language_name,))
        conn.commit()

def save_language_pair(english_sentence, foreign_sentence, language_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM languages WHERE language_name = ?', (language_name,))
        language_id = cursor.fetchone()[0]
        cursor.execute('''
            INSERT INTO language_pairs (english_sentence, foreign_sentence, language_id)
            VALUES (?, ?, ?)
        ''', (english_sentence, foreign_sentence, language_id))
        conn.commit()

def search_language_pairs(keyword=None, language_name=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = '''
            SELECT english_sentence, foreign_sentence, language_name
            FROM language_pairs 
            JOIN languages ON language_pairs.language_id = languages.id
            WHERE 1=1
        '''
        params = []
        
        if keyword and keyword.strip():
            query += ' AND (english_sentence LIKE ? OR foreign_sentence LIKE ?)'
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        if language_name and language_name != 'All':
            query += ' AND language_name = ?'
            params.append(language_name)
        
        cursor.execute(query, params)
        return cursor.fetchall()

# GUI Layout
def create_window():
    languages = fetch_languages()
    
    
    layout = [
        [sg.Text('Language:', font=(linux_font, 11)),
         sg.Combo(languages, key='-LANGUAGE-', size=(20, 1), font=(linux_font, 11)),
         sg.Button('Add Language', font=(linux_font, 11))],
        [sg.Text('New Language:', font=(linux_font, 11)),
         sg.Input(key='-NEW_LANGUAGE-', size=(20, 1), font=(linux_font, 11))],
        [sg.HorizontalSeparator()],
        [sg.Text('English Sentence:', font=(linux_font, 11)),
         sg.Input(key='-ENGLISH-', size=(40, 1), font=(linux_font, 11), 
                enable_events=True, focus=True)],
        [sg.Text('Foreign Sentence:', font=(linux_font, 11)),
         sg.Input(key='-FOREIGN-', size=(40, 1), font=(linux_font, 11),
                enable_events=True)],
        [sg.Button('Save Pair', bind_return_key=True, font=(linux_font, 11)), 
         sg.Button('Search', font=(linux_font, 11)), 
         sg.Button('Clear', font=(linux_font, 11))],
        [sg.HorizontalSeparator()],
        [sg.Text('Search Results:', font=(linux_font, 12, 'bold'))],
        [sg.Multiline(key='-OUTPUT-', size=(80, 15), font=(linux_font, 12),
                     autoscroll=True, expand_x=True, expand_y=True)],
        [sg.Text('Search Keyword:'), sg.Input(key='-KEYWORD-', size=(30, 1))],
        [sg.Text('Filter by Language:'), 
         sg.Combo(['All'] + languages, key='-SEARCH_LANGUAGE-', size=(20, 1))]
    ]
    
    return sg.Window('Language Memo App', layout, resizable=True, finalize=True)

# Main application
def main():
    initialize_database()
    window = create_window()

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        # Handle Enter key in text fields
        if event in ('-ENGLISH-', '-FOREIGN-'):
            if event.endswith('-') and values[event].endswith('\n'):
                window[event].update(values[event][:-1])
                event = 'Save Pair'

        # Add new language
        if event == 'Add Language':
            new_language = values['-NEW_LANGUAGE-'].strip()
            if not new_language:
                sg.popup_error('Please enter a language name', font=(linux_font, 11))
                continue
                
            location = get_location(window)
            try:
                add_language(new_language)
                updated_languages = fetch_languages()
                window['-LANGUAGE-'].update(values=updated_languages, value=new_language)
                window['-SEARCH_LANGUAGE-'].update(values=['All'] + updated_languages)
                window['-NEW_LANGUAGE-'].update('')
                sg.popup_auto_close(f'Added "{new_language}"!', auto_close_duration=0.8,
                                  font=(linux_font, 11), no_titlebar=True,
                                  background_color='#4CAF50', text_color='white',location=location)
            except sqlite3.IntegrityError:
                sg.popup_error(f'"{new_language}" already exists!', font=(linux_font, 11),location=location)

        # Save language pair
        if event == 'Save Pair':
            english = values['-ENGLISH-'].strip()
            foreign = values['-FOREIGN-'].strip()
            language = values['-LANGUAGE-']
            
            location = get_location(window)

            if not all([english, foreign, language]):
                sg.popup_error('All fields are required!', font=(linux_font, 11),location=location)
                window['-ENGLISH-'].set_focus()
                continue
                
            save_language_pair(english, foreign, language)
            window['-ENGLISH-'].update('')
            window['-FOREIGN-'].update('')
            
            # Auto-focus with double insurance
            window['-ENGLISH-'].set_focus()
            window.TKroot.after(100, lambda: window['-ENGLISH-'].set_focus())
            
            # Success notification
            sg.popup_auto_close('✓ Saved!', auto_close_duration=0.8,
                              font=(linux_font, 11), no_titlebar=True,
                              background_color='#4CAF50', text_color='white',location=location)

        # Search language pairs
        if event == 'Search':
            selected_language = values['-SEARCH_LANGUAGE-']
            keyword = values['-KEYWORD-'].strip() or None
            
            results = search_language_pairs(keyword, selected_language)
            
            if not results:
                window['-OUTPUT-'].update('No results found')
            else:
                output = '\n\n'.join(
                    f'English: {eng}\n{lang}: {forg}'
                    for eng, forg, lang in results
                )
                window['-OUTPUT-'].update(output)
            window['-ENGLISH-'].set_focus()

        # Clear results
        if event == 'Clear':
            window['-OUTPUT-'].update('')
            window['-KEYWORD-'].update('')
            window['-ENGLISH-'].set_focus()

    window.close()

if __name__ == '__main__':
    main()