"""

from lff to directory tree:
- get mapping glottocode -> Languoid from old tree
- assemble new directory tree
  - for each path component in lff:
    - create new dir
      - copy info file from old tree (possibly updating the name) or
      - create new info file
  - for each language in lff:
    - copy subtree rooted in language from old tree or
    - create new dir + info file
- rm old tree
- copy new tree
"""


def read_lff(p, level):
    path = None
    with io.open(p, encoding='utf8') as fp:
        for line in fp:
            if line.startswith('#'):
                continue
            if line.startswith('    '):
                assert path
                #
                # TODO: handle these errors, or fix them in glottolog before switching!
                #
                if path != 'ERROR [-unclassified-]':
                    yield Languoid.from_lff(path, line.strip(), level)
            else:
                path = line.strip()


def lff2tree(lff, tree=None, outdir='fromlff'):
    out = Path(outdir)
    out.mkdir()
    old_tree = {l.id: l for l in languoids_from_tree(tree)} if tree else {}

    nodes = set()
    languages = {}
    for lang in read_lff(lff, 'language'):
        groupdir = out
        languages[lang.id] = lang

        for name, id_, level in lang.lineage:
            groupdir = groupdir.joinpath('%s.%s' % (slug(name), id_))
            if not groupdir.exists():
                groupdir.mkdir()
                if id_ in old_tree:
                    group = old_tree[id_]
                    assert group.level == level
                    if name != group.name:
                        # rename a subgroup!
                        group.name = name
                    group.write_info(groupdir)
                else:
                    # TODO: create Languoid, write info file!
                    pass

            assert id_ in old_tree
            nodes.add(id_)

        assert lang.id in old_tree
        nodes.add(lang.id)
        old_lang = old_tree[lang.id]
        assert old_lang.level == lang.level
        if old_lang.name != lang.name:
            old_lang.name = lang.name
        langdir = groupdir.joinpath(lang.fname())
        langdir.mkdir()
        old_lang.write_info(langdir)

    for lang in read_lff(lff.replace('lff', 'dff'), 'dialect'):
        groupdir = out

        if not lang.lineage:
            # TODO: handle error of un-attached dialects!
            continue

        for name, id_, level in languages[lang.lineage[0][1]].lineage + lang.lineage:
            groupdir = groupdir.joinpath('%s.%s' % (slug(name), id_))
            if not groupdir.exists():
                groupdir.mkdir()
                if id_ in old_tree:
                    group = old_tree[id_]
                    assert group.level == level
                    if name != group.name:
                        # rename a subgroup!
                        group.name = name
                    group.write_info(groupdir)
                else:
                    # TODO: create Languoid, write info file!
                    pass

            assert id_ in old_tree
            nodes.add(id_)

        assert lang.id in old_tree
        nodes.add(lang.id)
        old_lang = old_tree[lang.id]
        assert old_lang.level == lang.level
        if old_lang.name != lang.name:
            old_lang.name = lang.name
        langdir = groupdir.joinpath(lang.fname())
        langdir.mkdir()
        old_lang.write_info(langdir)

    print len(nodes)


def tree2lff(tree):
    languoids = dict(dialect=defaultdict(list), language=defaultdict(list))
    nodes = {}

    for l in languoids_from_tree(tree, nodes=nodes):
        if l.level in languoids:
            languoids[l.level][l.lff_group()].append(l.lff_language())

    for level, languages in languoids.items():
        with io.open('%sff.txt' % level[0], 'w', encoding='utf8') as fp:
            fp.write('# -*- coding: utf-8 -*-\n')
            for path in sorted(languages):
                fp.write(path + '\n')
                for l in sorted(languages[path]):
                    fp.write(l + '\n')


if __name__ == "__main__":
    import sys
    tree2lff(sys.argv[1])