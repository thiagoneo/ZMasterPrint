# ZMasterPrint

Uma ferramenta simples e prática para gerar e imprimir etiquetas em impressoras Zebra usando código ZPL. Esta ferramenta foi desenvolvida visando atender principalmente rotinas do varejo.

## Funcionalidades
Há 4 abas principais, cada uma voltada a um tipo específico de impressão:

1. **Etiqueta de texto livre:** O usuário digita o texto, podendo adicionar e remover linhas de texto conforme necessário. O programa, então, gera o código ZPL que será enviado à impressora para impressão. O tamanho do texto se ajusta dinamicamente conforme a quantidade de linhas inseridas;
2. **Etiqueta de validade:** Indicada para produtos manipulados ou fabricados localmente. O usuário insere a data de fabricação e o prazo de validade, e é gerada a etiqueta com as datas de fabricação e validade formatadas;
3. **Info. produtos:** Ideal para imprimir detalhes de produtos, como **ingredientes**, **peso** e **validade**. O usuário seleciona o produto da lista, podendo cadastrar, editar ou remover produtos pelo menu `Editar > Cadastro de Produtos`;
5. **Imprimir arquivo ZPL:** Aqui o usuário pode imprimir diretamente arquivos ZPL salvos no computador.

Em todas essas abas é possível de escolher a quantidade de etiquetas que se deseja imprimir.

Mais detalhes sobre o uso e funcionalidades podem ser explorados diretamente no programa, que possui interface e intuitiva e simples de usar.

## Requisitos
- Impressora compatível com a linguagem ZPL (Zebra ou modelos de outros fabricantes compatíveis).
- Sistema operacional: Linux ou Windows.
- Python 3.x (para uso via código fonte).

## Licença
Consulte o arquivo [LICENSE](LICENSE) para mais informações.
