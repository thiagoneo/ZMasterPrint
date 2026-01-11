import os
import sys
import zpl
import socket
import tempfile
import platform
import subprocess
import unidecode
import confighelper
import cadprodhelper
from importlib.metadata import version
from datetime import datetime
from PyQt5 import QtWidgets as qt
from PyQt5 import QtGui as gui
from PyQt5.QtCore import Qt, QDate, QT_VERSION_STR
from pathlib import Path
from generated import resources_rc
from generated.ui_mainwindow import Ui_MainWindow as ui
from generated.ui_settingsdialog import Ui_Dialog as SettingsDialog
from generated.ui_cadprodutodlg import Ui_Dialog as CadProdutos
from generated.ui_aboutdlg import Ui_Dialog as InfoDialog
from datetime import datetime, date, timedelta

from __version__ import VERSION

if platform.system() == 'Windows':
    import win32print

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

class Window(qt.QMainWindow):

    def __init__(self):

        super(Window,self).__init__()

        if not os.path.isfile(confighelper.local_file):
            self.settings_dialog()
        self.ui = ui()
        self.ui.setupUi(self)
        self.setFixedSize(701, 455)
        self.setWindowTitle("Editor de etiquetas")
        self.lineCounter = 0
        self.ui.verticalLayout_2.setAlignment(Qt.AlignTop)
        self.add_line_edit()
        self.ui.dateFab.setDate(self.current_date())
        self.ui.dateFabPadaria_7.setDate(self.current_date())
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.btnPrint.clicked.connect(lambda: self.print_zpl_label(self.ui.tabWidget.currentIndex()))
        self.ui.actionAddLine.triggered.connect(self.add_line_edit)
        self.ui.actionRmLine.triggered.connect(self.remove_line_edit)
        self.ui.actionClearAll.triggered.connect(self.clear_all)
        self.ui.actionRmLine.setDisabled(True)
        self.ui.actionConfigs.triggered.connect(self.settings_dialog)
        self.ui.actionAbout.triggered.connect(self.info_dialog)
        self.ui.actionCadProd.triggered.connect(self.cad_prod_dialog)
        self.ui.tabWidget.tabBarClicked.connect(self.handle_tab_clicked)
        self.ui.btnPrintVal.clicked.connect(lambda: self.print_zpl_label(self.ui.tabWidget.currentIndex()))
        self.ui.btnPrintPadaria_7.clicked.connect(lambda: self.print_zpl_label(self.ui.tabWidget.currentIndex()))
        self.ui.actionQuit.triggered.connect(lambda: app.quit())
        self.ui.btnSelecArq.clicked.connect(self.selecionar_arquivo_zpl);
        self.ui.btnPrintArq.clicked.connect(self.imprimir_arquivo_zpl)
        # Atalhos de teclado
        self.atalhoImprimir = qt.QShortcut(gui.QKeySequence('Ctrl+Return'),self)
        self.atalhoImprimir1 = qt.QShortcut(gui.QKeySequence('Ctrl+Enter'),self)
        self.atalhoAdicionarLinha = qt.QShortcut(gui.QKeySequence('Ctrl+Shift+A'),self)
        self.atalhoRemoverLinha = qt.QShortcut(gui.QKeySequence('Ctrl+Shift+D'),self)
        self.atalhoLimparLinhas = qt.QShortcut(gui.QKeySequence('Ctrl+Shift+L'),self)
        self.atalhoImprimir.activated.connect(lambda: self.print_zpl_label(self.ui.tabWidget.currentIndex()))
        self.atalhoImprimir1.activated.connect(lambda: self.print_zpl_label(self.ui.tabWidget.currentIndex()))
        self.atalhoAdicionarLinha.activated.connect(self.add_line_edit)
        self.atalhoRemoverLinha.activated.connect(self.remove_line_edit)
        self.atalhoLimparLinhas.activated.connect(self.clear_all)
        # Colocar foco na primeira linha automaticamente
        self.linha0 = self.ui.verticalLayout_2.itemAt(0).widget()
        self.linha0.setFocus()
        if getattr(sys, 'frozen', False):
            self.exec_dir = os.path.dirname(sys.executable)
        elif __file__:
            self.exec_dir = os.path.dirname(__file__)
        os.chdir(self.exec_dir)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.label_dir = self.temp_dir.name + "/labels"
        self.receitas_dir = self.exec_dir + "/receitas"

        self.toolbar = qt.QToolBar()
        self.toolbar.addAction(self.ui.actionAddLine)
        self.toolbar.addAction(self.ui.actionRmLine)
        self.toolbar.addAction(self.ui.actionClearAll)
        self.ui.hLayoutToolbar.addWidget(self.toolbar)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Carregar dados de produtos
        self.dados_produtos = cadprodhelper.read_data()
        self.atualizar_combobox_produtos()
        self.ui.btnAtualizarCBProd.clicked.connect(self.atualizar_combobox_produtos)

        self.cadprod_dialog = qt.QDialog()
        self.cadprod_dialog.ui = CadProdutos()
        self.cadprod_dialog.ui.setupUi(self.cadprod_dialog)

        # Atualizar ícones de elementos da interface
        self.ui.actionAbout.setIcon(self.themed_icon("help-about", ":/icons/icons/help-about.svg"))
        self.ui.actionQuit.setIcon(self.themed_icon("application-exit", ":/icons/icons/application-exit.svg"))
        self.ui.actionCadProd.setIcon(self.themed_icon("document-edit", ":/icons/icons/document-edit.svg"))
        self.ui.actionConfigs.setIcon(self.themed_icon("settings", ":/icons/icons/configure.svg"))
        self.ui.btnAtualizarCBProd.setIcon(self.themed_icon("view-refresh", ":/icons/icons/view-refresh.svg"))
        self.ui.btnPrint.setIcon(self.themed_icon("document-print", ":/icons/icons/document-print.svg"))
        self.ui.btnPrintVal.setIcon(self.themed_icon("document-print", ":/icons/icons/document-print.svg"))
        self.ui.btnPrintPadaria_7.setIcon(self.themed_icon("document-print", ":/icons/icons/document-print.svg"))
        self.ui.btnPrintArq.setIcon(self.themed_icon("document-print", ":/icons/icons/document-print.svg"))
        self.ui.actionAddLine.setIcon(self.themed_icon("list-add", ":/icons/icons/list-add.svg"))
        self.ui.actionRmLine.setIcon(self.themed_icon("list-remove", ":/icons/icons/list-remove.svg"))
        self.ui.actionClearAll.setIcon(self.themed_icon("edit-clear-history", ":/icons/icons/edit-clear-history.svg"))

    def themed_icon(self, theme, resource):
        icon = gui.QIcon.fromTheme(theme)
        if icon.isNull():
            icon = gui.QIcon(resource)
        return icon

    def current_date(self):
        """Retorna a data atual"""
        today = QDate(date.today().year, date.today().month, date.today().day)
        return today

    def handle_tab_clicked(self, index):
        """Desativa botões da barra de ferramentas que devem ser usados apenas
        na aba 'Etiqueta comum'"""

        if index != 0:
            self.ui.actionAddLine.setDisabled(True)
            self.ui.actionRmLine.setDisabled(True)
            self.ui.actionClearAll.setDisabled(True)
        else:
            self.ui.actionClearAll.setEnabled(True)
            if self.lineCounter < 5:
                self.ui.actionAddLine.setEnabled(True)
            if self.lineCounter > 1:
                self.ui.actionRmLine.setEnabled(True)

    def gen_zpl_code(self,text_lines, modelo_etiqueta):
        """
        Gera código ZPL a partir do texto recebido
        
        text_lines (list): uma lista de elementos string, em que cada
        elemento dessa lista é uma linha do texto a ser impresso

        modelo_etiqueta (int): há três modelos de etiqueta disponíveis:
        0 - modelo de etiqueta padrão
        1 - modelo de etiqueta de validade
        2 - modelo de etiqueta produtos de padaria
        3 - modelo de etiqueta receita de produtos
        O usuário escolhe o modelo desejado clicando na aba correspondente
        """

        self.config = confighelper.read_config_file()
        self.printer = self.config['Device']['printer']
        self.labelWidth = int(self.config['Label']['width'])
        self.labelHeight = int(self.config['Label']['height'])
        self.ajuste_vertical = self.config['Label']['top_margin']
        self.ajuste_horizontal = self.config['Label']['left_margin']

        ajuste_y = int(self.ajuste_vertical)
        ajuste_x = int(self.ajuste_horizontal)

        l_height = self.labelHeight
        l_width = self.labelWidth
        l_dpmm = 8
        origin_x = 0
        font='0'
        orientation = 'N'
        line_width=None
        alig = 'L'
        max_line = 1
        line_spaces=0

        l = zpl.Label(l_height, l_width, l_dpmm)
        
        # Remover acentos e caracteres especiais
        for i in range(len(text_lines)):
            text_lines[i] = unidecode.unidecode(text_lines[i])

        if modelo_etiqueta == 1: # modelo etiqueta de validade
            font_height = 4
            font_width = 4
            line_spaces = 2.6
            origin_y = 8

        elif modelo_etiqueta == 2: # modelo etiqueta produtos de padaria
            max_line = 100
            line_width = (l_width - ajuste_x - 5)
            alig = 'J'
            font_height = 2.2
            font_width = 2.4
            line_spaces = 0
            origin_y = 3
        
        else: # modelo etiqueta = 0 (modelo etiqueta comum)
            mini_etiqueta = self.ui.boxMiniEtiqueta.isChecked()
            if mini_etiqueta:

                font_height = 4
                font_width = 4

                if len(text_lines) <=4:
                    line_spaces = 2.6
                    origin_y = 3
                    
                else:
                    line_spaces = 1
                    origin_y = 3

            else:
                line_spaces = 0
                if len(text_lines) == 1:
                    font_height = 17
                    font_width = 8
                    origin_y = 8
                    
                elif len(text_lines) == 2:
                    font_height = 12
                    font_width = 7
                    origin_y = 4
                    
                elif len(text_lines) == 3:
                    font_height = 8
                    font_width = 6
                    origin_y = 3
                    
                elif len(text_lines) == 4:
                    font_height = 6
                    font_width = 6
                    origin_y = 3
                    
                else:
                    font_height = 5
                    font_width = 5
                    origin_y = 3
        
        origin_y += ajuste_y
        origin_x += ajuste_x
        
        l.change_international_font(28)

        for i in range(len(text_lines)):
            l.origin(origin_x,origin_y)
            l.write_text(text_lines[i], font_height, font_width, font, orientation, line_width, max_line, line_spaces, alig)
            origin_y += (font_height + line_spaces)     # posicao nova linha
            l.endorigin()
        return (l.dumpZPL())

    def print_zpl_label(self, modelo_etiqueta):
        linhas_texto = []
        temp_output_file = None

        try:
            if modelo_etiqueta == 1:
                qtd = self.ui.spinQtdVal.value()
                dateVal = self.ui.dateFab.date().toPyDate()
                dateVal = dateVal + timedelta(days=float(self.ui.spinVal.value()))
                linha_fab = "Fab.: " + str(self.ui.dateFab.text())
                linha_val = "Val.: " + str('%02d' % dateVal.day) + "/" + str('%02d' % dateVal.month) + "/" + str('%04d' % dateVal.year)
                linhas_texto = [linha_fab, linha_val]

            elif modelo_etiqueta == 2:
                qtd = self.ui.spinQtdPadaria_7.value()
                data_fab_receita = self.ui.dateFabPadaria_7.date().toPyDate()
                linha_fab = "Fab.: " + str(self.ui.dateFabPadaria_7.text())
                cod_produto = self.ui.comboBoxProdutos.currentText().split(':')[0]
                for produto in self.dados_produtos["produtos"]:
                    if produto["codigo"] == cod_produto:
                        data_val_receita = data_fab_receita + timedelta(days=float(produto["validade_dias"]))
                        linha_val = "Val.: " + str('%02d' % data_val_receita.day) + "/" + str('%02d' % data_val_receita.month) + "/" + str('%04d' % data_val_receita.year)
                        peso = int(produto["peso"])
                        linha_peso = "Peso: " + str(peso) + "g"
                        receita_produto = "Ingredientes: " + produto["receita"]
                        linhas_texto.append(linha_fab)
                        linhas_texto.append(linha_val)
                        linhas_texto.append(linha_peso)
                        linhas_texto.append(receita_produto)

            else:
                qtd = self.ui.spinQtd.value()
                for i in range(self.lineCounter):
                    widget_item = self.ui.verticalLayout_2.itemAt(i)
                    widget = widget_item.widget()
                    linhas_texto.append(widget.text())
            
            if qtd <= 1:
                mensagem = "Enviando 1 etiqueta para impressão..."
            else:
                mensagem = f"Enviando {qtd} etiquetas para impressão..."

            zplCode = self.gen_zpl_code(linhas_texto, modelo_etiqueta)
            zplCode = str(zplCode).replace('^CI', '\n^CI')
            zplCode = zplCode.replace('^FO', '\n^FO')
            zplCode = zplCode.replace('^XZ', '\n^PQ' + str(qtd) + ',0,1,N\n^XZ')

            if not os.path.exists(self.label_dir):
                os.makedirs(self.label_dir)

            temp_output_file = self.label_dir + "/temp_output_file.tmp"
            arq = open(temp_output_file, "wt")
            arq.write(zplCode)
            arq.close()

            now = datetime.now()
            hostname = socket.gethostname()
            dt = str(now).replace(" ", "_")
            file = self.label_dir + "/" + hostname + "_" + dt
            file = file.replace(":", "-").replace(".", "-") + ".zpl"

        except Exception as e:
            print(f"Erro ao preparar etiqueta: {e}")
            return

        try:
            if platform.system() == 'Linux':
                command = '''file=''' + file + ''' ; cat ''' + temp_output_file + ''' > "${file}" ;\
                lp -o raw -d ''' + str(self.printer) + ''' "${file}"'''
                print(mensagem)
                os.system(command)

            elif platform.system() == 'Windows':
                temp_output_file = temp_output_file.replace("/", "\\")
                file = file.replace("/", "\\")
                file = "C:" + file[2:]
                print(mensagem)
                self.chamada_impressao_windows(self.printer, temp_output_file)

            else:
                print("S.O. não suportado!")

        except Exception as e:
            print(f"Erro durante a impressão: {e}")

        finally:
            if temp_output_file and os.path.exists(temp_output_file):
                os.remove(temp_output_file)
    
    def add_line_edit(self):
        if self.lineCounter < 5:
            self.newLineEdit = qt.QLineEdit(self.ui.verticalLayoutWidget)
            self.newLineEdit.setObjectName("lineEdit" + str(self.lineCounter))
            self.ui.verticalLayout_2.addWidget(self.newLineEdit)
            self.lineCounter += 1
            if self.ui.actionRmLine.isEnabled() == False:
                self.ui.actionRmLine.setEnabled(True)
        if self.lineCounter >= 5:
            self.ui.actionAddLine.setDisabled(True)
    
    def remove_line_edit(self):
        if self.lineCounter > 1:
            self.lineToRemove = self.ui.verticalLayout_2.itemAt(self.lineCounter - 1)
            self.widget = self.lineToRemove.widget()
            self.widget.deleteLater()
            self.lineCounter -= 1
            if self.ui.actionAddLine.isEnabled() == False:
                self.ui.actionAddLine.setEnabled(True)
        if self.lineCounter <= 1:
            self.ui.actionRmLine.setDisabled(True)
    
    def clear_all(self):
        for i in range(self.lineCounter):
            widget_item = self.ui.verticalLayout_2.itemAt(i)
            widget = widget_item.widget()
            widget.clear()
    
    def settings_dialog(self):
        dialog = qt.QDialog()
        dialog.ui = SettingsDialog()
        dialog.ui.setupUi(dialog)
        dialog.ui.btnAtualizarCBImpressoras.setIcon(self.themed_icon("view-refresh", ":/icons/icons/view-refresh.svg"))
        dialog.setFixedSize(470,430)
        dialog.setWindowTitle("Configurações")
        dialog.ui.comboBoxImpressoras.clear()
        dialog.ui.comboBoxImpressoras.addItems(self.listar_impressoras())
        if os.path.isfile(confighelper.local_file):
            config = confighelper.read_config_file()
            labelWidth = int(config['Label']['width'])
            labelHeight = int(config['Label']['height'])
            topMargin = config['Label']['top_margin']
            leftMargin = config['Label']['left_margin']
            printer = config['Device']['printer']
            zpl_dir = config['ZPLDir']['directory']
            dialog.ui.spinLabelWidth.setValue(int(labelWidth))
            dialog.ui.spinLabelHeight.setValue(int(labelHeight))
            dialog.ui.spinVerticalAdj.setValue(int(topMargin))
            dialog.ui.spinHorizontalAdj.setValue(int(leftMargin))
            # dialog.ui.linePrinter.setText(printer)
            dialog.ui.comboBoxImpressoras.setCurrentText(printer)
            dialog.ui.lePastaZPL.setText(zpl_dir)
        else:
            dialog.ui.spinLabelWidth.setValue(60)
            dialog.ui.spinLabelHeight.setValue(30)
            dialog.ui.spinVerticalAdj.setValue(0)
            dialog.ui.spinHorizontalAdj.setValue(0)
        
        dialog.ui.btnAtualizarCBImpressoras.clicked.connect(
            lambda: (
                dialog.ui.comboBoxImpressoras.clear(),
                dialog.ui.comboBoxImpressoras.addItems(self.listar_impressoras())
            )
        )
        
        dialog.ui.btnSelecPastaZPL.clicked.connect(
            lambda: dialog.ui.lePastaZPL.setText(qt.QFileDialog.getExistingDirectory(self, "Selecionar uma pasta"))
            )

        dialog.ui.btnSave.accepted.connect(
            lambda: confighelper.write_config_file(
                str(dialog.ui.comboBoxImpressoras.currentText()),
                str(dialog.ui.spinLabelHeight.value()),
                str(dialog.ui.spinLabelWidth.value()),
                str(dialog.ui.spinVerticalAdj.value()),
                str(dialog.ui.spinHorizontalAdj.value()),
                str(dialog.ui.lePastaZPL.text())
            )
        )

        dialog.ui.btnSave.accepted.connect(dialog.close)

        dialog.ui.btnSave.accepted.connect(dialog.close)
        dialog.ui.btnSave.accepted.connect(self.show_config_saved_dialog)
        dialog.ui.btnSave.rejected.connect(dialog.close)
        dialog.exec_()

    def show_config_saved_dialog(self):
        dlg = qt.QMessageBox(self)
        dlg.setIcon(qt.QMessageBox.Information)
        dlg.setText("Configuração salva com sucesso!")
        dlg.exec()

    def load_about_requirements_html(self) -> str:
        if getattr(sys, "frozen", False):
            # Executável PyInstaller
            base_path = Path(sys._MEIPASS)
        else:
            # Código fonte normal
            base_path = Path(__file__).resolve().parent
        html_path = base_path / "generated" / "about_reqs.html"
        return html_path.read_text(encoding="utf-8")

    def info_dialog(self):
        dialog = qt.QDialog()
        dialog.ui = InfoDialog()
        dialog.ui.setupUi(dialog)
        dialog.ui.labelVersion.setText(VERSION)
        dialog.setFixedSize(361,420)
        dialog.setWindowTitle("Sobre o Editor de etiquetas")
        dialog.ui.btnFechar.clicked.connect(dialog.close)
        dialog.ui.btnFechar.setIcon(self.themed_icon("dialog-close", ":/icons/icons/dialog-close.svg"))
        components_str = self.load_about_requirements_html()
        python_str = dialog.ui.labelPython.text()
        qt_str = dialog.ui.labelQt.text()
        python_str = python_str.replace("&lt;python_version&gt;", PYTHON_VERSION)
        qt_str = qt_str.replace("&lt;qt_version&gt;", QT_VERSION_STR)
        dialog.ui.labelPython.setText(python_str)
        dialog.ui.labelQt.setText(qt_str)
        dialog.ui.textBrowserComponents.setHtml(components_str)
        dialog.ui.textBrowserComponents.setOpenExternalLinks(True)
        dialog.ui.labelAbout.setOpenExternalLinks(True)

        dialog.exec_()

    def cad_prod_dialog(self):
        dialog = self.cadprod_dialog
        # dialog.ui = CadProdutos()
        # dialog.ui.setupUi(dialog)
        # dialog.setFixedSize(402,407)
        dialog.setWindowTitle("Cadastro de produtos")
        self.atualizar_lista_produtos()
        self.limpar_campos()

        dialog.ui.btnNovoProd.setIcon(self.themed_icon("list-add", ":/icons/icons/list-add.svg"))
        dialog.ui.btnEditarProd.setIcon(self.themed_icon("document-edit", ":/icons/icons/document-edit.svg"))
        dialog.ui.btnExcluirProd.setIcon(self.themed_icon("edit-delete", ":/icons/icons/edit-delete.svg"))
        dialog.ui.btnCancelar.setIcon(self.themed_icon("dialog-cancel", ":/icons/icons/dialog-cancel.svg"))
        dialog.ui.btnSalvar.setIcon(self.themed_icon("document-save", ":/icons/icons/document-save.svg"))

        dialog.ui.listaProdutos.itemSelectionChanged.connect(self.seleciona_item)
        dialog.ui.listaProdutos.itemSelectionChanged.connect(self.atualizar_campos_cadproduto)
        dialog.ui.btnSalvar.clicked.connect(self.salvar_produto)
        dialog.ui.btnSalvar.clicked.connect(self.limpar_campos)
        dialog.ui.btnCancelar.clicked.connect(self.cancelar)
        dialog.ui.btnCancelar.clicked.connect(self.limpar_campos)

        dialog.ui.btnEditarProd.clicked.connect(self.editar_item)
        dialog.ui.btnNovoProd.clicked.connect(self.cadastrar_novo_item)
        dialog.ui.btnExcluirProd.clicked.connect(self.excluir_item)

        self.disable_widgets()

        dialog.exec_()
    
    def disable_widgets(self):
        dialog = self.cadprod_dialog
        # Tornar todos os campos não-editáveis por padrão (serão editáveis apenas ao clicar no botao "editar" ou "novo")
        dialog.ui.leCodigo.setEnabled(False)
        dialog.ui.leDescricao.setEnabled(False)
        dialog.ui.leValidade.setEnabled(False)
        dialog.ui.leReceita.setEnabled(False)
        dialog.ui.lePeso.setEnabled(False)
        
        # Desabilitar botoes
        dialog.ui.btnEditarProd.setEnabled(False)
        dialog.ui.btnExcluirProd.setEnabled(False)
        dialog.ui.btnSalvar.setEnabled(False)
        dialog.ui.btnCancelar.setEnabled(False)

    def seleciona_item(self):
        dialog = self.cadprod_dialog
        # Habilitar botões "Editar item" e "Excluir item"
        dialog.ui.btnEditarProd.setEnabled(True)
        dialog.ui.btnExcluirProd.setEnabled(True)
        
        # Obtém o item selecionado na lista
        item_selecionado = dialog.ui.listaProdutos.currentItem()
        if item_selecionado:
            # Obtém o texto do item selecionado
            texto_item = item_selecionado.text()
            # Extrai o código do produto do texto do item (pode ser necessário ajustar essa parte dependendo do formato)
            self.codigo_produto = texto_item.split(':')[0].strip()

    def editar_item(self):
        dialog = self.cadprod_dialog
        # Habilitar campos para edição
        dialog.ui.btnSalvar.setEnabled(True)
        dialog.ui.btnCancelar.setEnabled(True)
        dialog.ui.listaProdutos.setEnabled(False)
        dialog.ui.leDescricao.setEnabled(True)
        dialog.ui.leValidade.setEnabled(True)
        dialog.ui.leReceita.setEnabled(True)
        dialog.ui.lePeso.setEnabled(True)
        dialog.ui.btnNovoProd.setEnabled(False)
        dialog.ui.btnEditarProd.setEnabled(False)
        dialog.ui.btnExcluirProd.setEnabled(False)
    
    def cadastrar_novo_item(self):
        dialog = self.cadprod_dialog
        dialog.ui.listaProdutos.clearSelection()
        self.limpar_campos()
        dialog.ui.leCodigo.setEnabled(True)
        self.editar_item()
        dialog.ui.btnSalvar.setEnabled(True)
        dialog.ui.btnCancelar.setEnabled(True)
        dialog.ui.btnNovoProd.setEnabled(False)
        dialog.ui.btnEditarProd.setEnabled(False)
        dialog.ui.btnExcluirProd.setEnabled(False)

    def excluir_item(self):
        dialog = self.cadprod_dialog
        if self.msg_excluir_item():
            produto_selecionado = None

            for produto in self.dados_produtos["produtos"]:
                if produto["codigo"] == self.codigo_produto:
                    self.dados_produtos["produtos"].remove(produto)
                    break
            cadprodhelper.write_data(self.dados_produtos)
            self.atualizar_lista_produtos()
    
    def msg_excluir_item(self):
        dlg = qt.QMessageBox(self)
        dlg.setIcon(qt.QMessageBox.Question)
        resposta = dlg.question(self, '', "Deseja realmente excluir este item?", dlg.Yes | dlg.No)
        if resposta == dlg.Yes:
            return True
        else:
            return False

    def atualizar_campos_cadproduto(self):
        # dialog = qt.QDialog()
        dialog = self.cadprod_dialog

        # Procura o produto correspondente no arquivo JSON
        produto_selecionado = None
        for produto in self.dados_produtos["produtos"]:
            if produto["codigo"] == self.codigo_produto:
                produto_selecionado = produto
                break
         
        # Atualiza os campos com as informações do produto selecionado
        if produto_selecionado:
            dialog.ui.leCodigo.setText(produto_selecionado["codigo"])
            dialog.ui.leDescricao.setText(produto_selecionado["descricao"])
            if produto_selecionado["validade_dias"] == "":
                produto_selecionado["validade_dias"] = "0"
            if produto_selecionado["peso"] == "":
                produto_selecionado["peso"] = "0"
            dialog.ui.leValidade.setValue(int(produto_selecionado["validade_dias"]))
            dialog.ui.leReceita.setPlainText(produto_selecionado["receita"])
            dialog.ui.lePeso.setValue(int(produto_selecionado["peso"]))
        else:
            # Limpa os campos se o produto não for encontrado
            dialog.ui.leCodigo.clear()
            dialog.ui.leDescricao.clear()
            dialog.ui.leValidade.clear()
            dialog.ui.leReceita.clear()
            dialog.ui.lePeso.clear()

    def msg_erro_cadastro_produto(self, msg_erro):
        dlg = qt.QMessageBox(self)
        dlg.setIcon(qt.QMessageBox.Critical)
        dlg.setText(msg_erro)
        dlg.exec()
    
    def salvar_produto(self):
        dialog = self.cadprod_dialog

        msg_erro = 'ERRO:'

        erro_cadastro = False
        codigo_duplicado = False
        descricao = dialog.ui.leDescricao.text()
        receita = dialog.ui.leReceita.toPlainText()
        validade_dias = dialog.ui.leValidade.text()
        peso = dialog.ui.lePeso.text()

        # Se o campo leCodigo estiver habilitado, significa que será feito o cadastro de um novo produto
        if dialog.ui.leCodigo.isEnabled():
            if dialog.ui.leCodigo.text() == "":
                erro_cadastro = True
                msg_erro += '\nO campo "Código" não pode ficar vazio! Por favor, preencha-o.'
            else:
                codigo = str(int(dialog.ui.leCodigo.text()))

                # Verificar se o codigo informado já existe
                produto_selecionado = None
                for produto in self.dados_produtos["produtos"]:
                    if produto["codigo"] == codigo:
                        codigo_duplicado = True
                        break
                if codigo_duplicado:
                    erro_cadastro = True
                    msg_erro += '\nO código de produto informado já existe! Informe um novo código.'
                if descricao == "":
                    erro_cadastro = True
                    msg_erro += '\nO campo "Descrição" não pode ficar vazio! Por favor, preencha-o.'
                if receita == "":
                    erro_cadastro = True
                    msg_erro += '\nO campo "Receita" não pode ficar vazio! Por favor, preencha-o.'
            
            if erro_cadastro:
                self.msg_erro_cadastro_produto(msg_erro)

            else:
                novo_produto = {
                    "codigo": codigo,
                    "descricao": descricao,
                    "receita": receita,
                    "validade_dias": validade_dias,
                    "peso": peso
                }
                self.dados_produtos["produtos"].append(novo_produto)
        
        else:
            # Procura o produto correspondente no arquivo JSON
            produto_selecionado = None
            for produto in self.dados_produtos["produtos"]:
                if produto["codigo"] == self.codigo_produto:
                    produto_selecionado = produto
                    break
            
            if descricao == "":
                erro_cadastro = True
                msg_erro += '\nO campo "Descrição" não pode ficar vazio! Por favor, preencha-o.'
            if receita == "":
                erro_cadastro = True
                msg_erro += '\nO campo "Receita" não pode ficar vazio! Por favor, preencha-o.'
            
            if erro_cadastro:
                self.msg_erro_cadastro_produto(msg_erro)

            else:
                produto_selecionado["descricao"] = descricao
                produto_selecionado["receita"] = receita
                produto_selecionado["validade_dias"] = validade_dias
                produto_selecionado["peso"] = peso

        cadprodhelper.write_data(self.dados_produtos)
        
        self.disable_widgets()
        self.atualizar_lista_produtos()
        dialog.ui.listaProdutos.setEnabled(True)
        dialog.ui.btnNovoProd.setEnabled(True)
    
    def cancelar(self):
        dialog = self.cadprod_dialog
        self.disable_widgets()
        self.atualizar_lista_produtos()
        dialog.ui.listaProdutos.setEnabled(True)
        dialog.ui.btnNovoProd.setEnabled(True)
    
    def atualizar_lista_produtos(self):
        dialog = self.cadprod_dialog
        dialog.ui.listaProdutos.clear()
        for produto in self.dados_produtos["produtos"]:
            codigo_produto = produto["codigo"]
            descricao_produto = produto["descricao"]
            item = qt.QListWidgetItem(f"{codigo_produto}: {descricao_produto}")
            dialog.ui.listaProdutos.addItem(item)
    
    def limpar_campos(self):
        dialog = self.cadprod_dialog
        dialog.ui.leCodigo.clear()
        dialog.ui.leDescricao.clear()
        dialog.ui.leValidade.setValue(0)
        dialog.ui.leReceita.clear()
        dialog.ui.lePeso.setValue(0)

    def atualizar_combobox_produtos(self):
        self.ui.comboBoxProdutos.clear()
        for produto in self.dados_produtos["produtos"]:
            str_produto = (str(produto["codigo"]) + ": " + str(produto["descricao"]))
            self.ui.comboBoxProdutos.addItem(str_produto)
            # codigo = str_produto.split(':')[0]
    
    def selecionar_arquivo_zpl(self):
        self.config = confighelper.read_config_file()
        self.printer = self.config['Device']['printer']
        self.labelWidth = int(self.config['Label']['width'])
        self.labelHeight = int(self.config['Label']['height'])
        self.ajuste_vertical = self.config['Label']['top_margin']
        self.ajuste_horizontal = self.config['Label']['left_margin']
        self.default_zpl_folder = self.config['ZPLDir']['directory']
        self.arquivo_zpl = qt.QFileDialog.getOpenFileName(self, "Abrir", self.default_zpl_folder, "Arquivos ZPL (*.zpl)")
        if self.arquivo_zpl:
            self.ui.leSelecArq.setText(self.arquivo_zpl[0])
    
    def listar_impressoras_linux(self):
        try:
            result = subprocess.run(
                ["lpstat", "-a"],
                capture_output=True,
                text=True,
                check=True  # Lança exceção se o comando falhar
            )
            printers = []
            for line in result.stdout.splitlines():
                printers.append(line.split()[0])
            return printers
        except FileNotFoundError:
            print("Erro: comando 'lpstat' não encontrado. Verifique se o CUPS está instalado.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao listar impressoras no Linux: {e}")
        except Exception as e:
            print(f"Erro inesperado no Linux: {e}")
        return []

    def listar_impressoras_windows(self):
        if win32print is None:
            print("Erro: módulo 'win32print' não disponível. Instale pywin32.")
            return []
        try:
            printers = []
            for printer in win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            ):
                printers.append(printer[2])
            return printers
        except Exception as e:
            print(f"Erro ao listar impressoras no Windows: {e}")
            return []
    
    def listar_impressoras(self):
        sistema = platform.system()
        if sistema == 'Linux':
            return self.listar_impressoras_linux()
        elif sistema == 'Windows':
            return self.listar_impressoras_windows()
        else:
            print(f"S.O. '{sistema}' não suportado!")
            return []

    def chamada_impressao_windows(self, impressora, arquivo):
        try:
            with open(arquivo, 'rb') as f:
                dados = f.read()
            hPrinter = win32print.OpenPrinter(impressora)
        except Exception as e:
            print(f"Erro ao preparar impressão: {e}")
            return
        try:
            job_info = ("label", None, "RAW")
            win32print.StartDocPrinter(hPrinter, 1, job_info)
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, dados)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        except Exception as e:
            print(f"Erro durante a impressão: {e}")
        finally:
            win32print.ClosePrinter(hPrinter)
    
    def imprimir_arquivo_zpl(self):

        try:
            qtd = self.ui.spinQtdArq.value()
            self.config = confighelper.read_config_file()
            self.printer = self.config['Device']['printer']
            self.labelWidth = int(self.config['Label']['width'])
            self.labelHeight = int(self.config['Label']['height'])
            self.ajuste_vertical = self.config['Label']['top_margin']
            self.ajuste_horizontal = self.config['Label']['left_margin']
            arquivo = self.ui.leSelecArq.text()
            if qtd <= 1:
                mensagem = "Enviando 1 etiqueta para impressão..."
            else:
                mensagem = f"Enviando {qtd} etiquetas para impressão..."
        except Exception as e:
            print(f"Erro ao preparar impressão do arquivo: {e}")
            return

        try:
            if platform.system() == 'Linux':
                command = '''lp -o raw -d ''' + str(self.printer) + " -n " + str(qtd) + " " + arquivo
                print(mensagem)
                os.system(command)
            elif platform.system() == 'Windows':
                print(mensagem)
                self.chamada_impressao_windows(self.printer, arquivo)
            else:
                print("S.O. não suportado!")
            # self.temp_dir.cleanup()
        except Exception as e:
            print(f"Erro durante a impressão do arquivo: {e}")

# Run Application

app = qt.QApplication([])
application = Window()
application.show()
app.exec()
