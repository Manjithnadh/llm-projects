from flask import render_template ,Flask,request

from transformers import AutoModelForCausalLM,AutoTokenizer

import wikipedia

app=Flask(__name__)
model_name='gpt2'

tokenize=AutoTokenizer.from_pretrained(model_name)

model=AutoModelForCausalLM.from_pretrained(model_name)

@app.route('/',methods=['POST','GET'])
def index():
    response=''
    suggestion=[]

    if request.method=='POST':
        topic=request.form['user_input']

        try:
            wiki_content=wikipedia.summary(topic)
        except wikipedia.exceptions.DisambiguationError as e:
            suggestion=e.options
            wiki_content=None
        except wikipedia.exceptions.PageError:
            wiki_content='sorry page is not available'

        if wiki_content:
            inputs = tokenize.encode(wiki_content,return_tensors='pt')
            outputs = model.generate(inputs)
            response = tokenize.decode(outputs[0],skip_special_tokens=True)
    return render_template('index.html',response=response,suggestion=suggestion)


if __name__=='__main__':
    app.run(debug=True)
