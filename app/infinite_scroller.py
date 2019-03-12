from faker import Faker
from flask import Blueprint, jsonify, request

from utils import sanitize_param_num


bp = Blueprint('infinite_scroller', __name__, url_prefix='/infinite-scroller')
faker = Faker()


@bp.route('/', methods=['GET'])
def index():
    data = []
    n_paragraphs = sanitize_param_num(request, 'paragraphs', 3, 1, 10)
    n_entries = sanitize_param_num(request, 'entries', 10, 1, 100)

    for _ in range(n_entries):
        gen_desc_sentence = lambda: faker.sentence(nb_words=15, variable_nb_words=True)
        description = [ gen_desc_sentence() for _ in range(n_paragraphs) ]

        data.append({
            'title': faker.sentence(nb_words=6, variable_nb_words=True)[:-1],
            'image_url': f'https://picsum.photos/200/120/?random',
            'description': description,
        })

    return jsonify(data)
