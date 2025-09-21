from flask import Flask, request, render_template
from karma.encode_decode import parse_sentence
from collections import deque
import argparse
from waitress import serve

parser = argparse.ArgumentParser()
parser.add_argument("--port", default="5000") 
args = parser.parse_args()
port: str = args.port

app = Flask(__name__)

# Keep the last 5 sentences and cache their results
history = deque(maxlen=5)
# sentence -> (result list of lists in traditional form, result list of lists in mofo form)
results_cache: dict[str, tuple[list[list[str]], list[list[str]]]] = {}  

@app.route('/', methods=['GET', 'POST'])
def home():
    parsed_list_str, parsed_list_mofo = None, None
    view = request.form.get('view', 'str')
    sentence = request.form.get('sentence', '')
    if request.method == 'POST':
        if sentence:
            # check cache
            if sentence in results_cache:
                parsed_list_str, parsed_list_mofo = results_cache[sentence]
            else:
                parsed = parse_sentence(sentence.lower())
                parsed_list_str = parsed.list_str
                parsed_list_mofo = parsed.list_mofo_str
                results_cache[sentence] = (parsed_list_str, parsed_list_mofo)
            # update history
            if sentence in history:
                history.remove(sentence)
            history.appendleft(sentence)
            # print(list(history))
    return render_template('index.html', 
                           result_str=parsed_list_str,
                           result_mofo=parsed_list_mofo, 
                           sentence=sentence, 
                           history=list(history), 
                           view=view)

if __name__ == '__main__':
    host = "127.0.0.1"
    print(f"Serving on http://{host}:{port} ...")
    serve(app, port=port)
