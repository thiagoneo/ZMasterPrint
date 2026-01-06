import sys
# ...existing code...
def listar_bibliotecas():
    linhas = []
    try:
        from importlib.metadata import packages_distributions, version, PackageNotFoundError
    except Exception:
        return "<i>informação de pacotes indisponível</i>"
    pkg_map = packages_distributions()
    seen = set()
    for mod in sorted(sys.modules.keys()):
        base = mod.split('.', 1)[0]
        if not base or base in seen:
            continue
        dists = pkg_map.get(base)
        if dists:
            for dist in dists:
                if dist in seen:
                    continue
                try:
                    ver = version(dist)
                    linhas.append(f'<a href="https://pypi.org/project/{dist}/"><b><span style=" text-decoration: underline; color:#0850bd;">{dist}</span></b></a> {ver}')
                except PackageNotFoundError:
                    linhas.append(f'{dist} (não instalado)')
                seen.add(dist)
        else:
            try:
                ver = version(base)
                linhas.append(f'<a href="https://pypi.org/project/{base}/"><b><span style=" text-decoration: underline; color:#0850bd;">{base}</span></b></a> {ver}')
                seen.add(base)
            except PackageNotFoundError:
                pass
    if not linhas:
        return "<i>Nenhuma dependência detectada</i>"
    return "<br>\n".join(linhas)
# ...existing code...

print(listar_bibliotecas())