from dataclasses import dataclass
import json
import more_itertools as mit

@dataclass
class GhostDb:
    path: str

    def __post_init__(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)['db'][0]
        self.tags = self._get_tags()

    def _get_tags(self):
        return {tag['id']: tag['name'] for tag in self.db['data']['tags']}
    
    @staticmethod
    def pprint(jsonable: dict):
        print(json.dumps(jsonable, indent=4, ensure_ascii=False))

    def get_formatted_posts(self, chunk_size, p_padding: float):
        posts = [post for post in self.db['data']['posts']]
        tags = [tag for tag in self.db['data']['posts_tags']]
        tags += (len(posts) - len(tags)) * [None]
        assert len(posts) == len(tags)

        formatted_post = {}
        for post in posts:
            if post['plaintext'] is None:
                continue
            plaintext = list(mit.windowed(
                seq=post['plaintext'].split(), 
                n=chunk_size,
                step=int(chunk_size * (1 - p_padding)),
            ))
            plaintext = [' '.join(p) for p in [list(filter(None, w)) for w in plaintext]]

            formatted_post[post['id']] = {
                'id': post['id'],
                'title': post['title'],
                'plaintext': plaintext,
                'tags': [],
                'created_at': post['created_at'],
            }
        for tag in tags:
            if tag is None:
                continue
            formatted_post[tag['post_id']]['tags'].append(self.tags[tag['tag_id']])
        return [f for f in formatted_post.values()]
    


g = GhostDb('data/coins/collectprime-blog.ghost.2025-02-02-15-47-58.json')

for i in range(1):
    g.pprint(g.get_formatted_posts(10, 0.3)[i]['plaintext'])