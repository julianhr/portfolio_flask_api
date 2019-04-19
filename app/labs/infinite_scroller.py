from faker import Faker
from flask import Blueprint, jsonify, request

from utils import clamp_param_num


bp = Blueprint('infinite_scroller', __name__, url_prefix='/labs')
faker = Faker()


@bp.route('/infinite-scroller', methods=['GET'])
def index():
    data = []
    n_paragraphs = clamp_param_num(request, 'paragraphs', 3, 1, 5)
    n_entries = clamp_param_num(request, 'entries', 10, 1, 10)
    themes = 'nature ice sunset people pets water volcano desert flowers'.split()

    for i in range(n_entries):
        gen_desc_sentence = lambda: faker.sentence(nb_words=15, variable_nb_words=True)
        description = [ gen_desc_sentence() for _ in range(n_paragraphs) ]
        theme = themes[i % len(themes)]

        data.append({
            'title': faker.sentence(nb_words=6, variable_nb_words=True)[:-1],
            'image_url': f'https://source.unsplash.com/random/150x100/?{theme}',
            'description': description,
        })

    return jsonify(data)
