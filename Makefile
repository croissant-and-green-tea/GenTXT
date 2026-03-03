.PHONY: help all install dev build clean run headless lint format \
        docs serve-docs deploy-docs install-system uninstall-system \
        test test-unit test-integration test-nr test-cov \
        update-snapshots generate-fixture-ods

PYTHON    := python3
PIP       := pip
SRC_DIR   := src
DIST_DIR  := dist
BUILD_DIR := build
SPEC_FILE := GenTxt.spec
EXEC_NAME := GenTXT

# === Aide =====================================================================

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# === All ======================================================================

all: dev lint test-cov build docs ## Lint + tests + couverture + build + docs (pipeline complet)

# === Environnement ============================================================

install: ## Installe les dépendances runtime
	$(PIP) install -r requirements.txt

dev: ## Installe les dépendances dev (runtime + outils)
	$(PIP) install -r requirements-dev.txt

docs-deps: ## Installe les dépendances de documentation
	$(PIP) install -r requirements-docs.txt

# === Run ======================================================================

run: ## Lance l'application en mode GUI
	$(PYTHON) $(SRC_DIR)/main.py

headless: ## Lance en mode headless dans le répertoire courant
	$(PYTHON) $(SRC_DIR)/main.py --headless

# === Qualité ==================================================================

lint: ## Lint avec ruff
	ruff check $(SRC_DIR)

format: ## Formate avec ruff
	ruff format $(SRC_DIR)

typecheck: ## Vérifie les types avec mypy
	mypy $(SRC_DIR)/gentxt/core.py $(SRC_DIR)/gentxt/config.py

# === Tests ====================================================================

test: ## Lance la suite de tests complète
	pytest tests/ -v

test-unit: ## Lance uniquement les tests unitaires
	pytest tests/unit/ -v

test-integration: ## Lance uniquement les tests d'intégration
	pytest tests/integration/ -v

test-nr: ## Lance uniquement les tests de non-régression
	pytest tests/non_regression/ -v

test-cov: ## Lance les tests avec rapport de couverture HTML
	pytest tests/ --cov=src/gentxt --cov-report=html --cov-report=term-missing

update-snapshots: ## Régénère les golden files de non-régression
	UPDATE_SNAPSHOTS=1 pytest tests/non_regression/ -v

generate-fixture-ods: ## Génère le fichier table.ods vide dans la fixture project_simple
	$(PYTHON) -c "\
from odf.opendocument import OpenDocumentSpreadsheet; \
doc = OpenDocumentSpreadsheet(); \
doc.save('tests/non_regression/fixtures/project_simple/data/table.ods'); \
print('table.ods généré')"

# === Build ====================================================================

build: clean install ## Build l'exécutable PyInstaller
	pyinstaller $(SPEC_FILE)
	@echo "→ Exécutable : $(DIST_DIR)/$(EXEC_NAME)"

clean: ## Supprime les artefacts de build et caches Python
	rm -rf $(BUILD_DIR) $(DIST_DIR) site/ htmlcov/ .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# === Installation système =====================================================

install-system: build ## Installe GenTxt dans /opt/gentxt
	chmod +x install_gentxt.sh && ./install_gentxt.sh

uninstall-system: ## Désinstalle GenTxt du système
	chmod +x uninstall_gentxt.sh && ./uninstall_gentxt.sh

# === Documentation ============================================================

docs-assets: ## Synchronise les assets doc depuis src/icons/
	mkdir -p docs/assets
	cp src/icons/icons.png docs/assets/icons.png

docs: docs-deps docs-assets ## Build la documentation MkDocs
	mkdocs build

serve-docs: docs-deps ## Sert la doc en local (http://127.0.0.1:8000)
	mkdocs serve

deploy-docs: docs-deps ## Déploie la doc sur GitHub Pages
	mkdocs gh-deploy --force