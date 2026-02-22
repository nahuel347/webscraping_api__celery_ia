from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

class CorfoScraper:
    async def _get_data(self):
        # 1. Configuración de 'Sigilo' para evitar el ERR_CONNECTION_REFUSED
        browser_config = BrowserConfig(
            headless=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        # 2. Script para cargar los 57 programas (Hacer clic en 'Cargar más')
        js_load_all = """
        async () => {
            const sleep = ms => new Promise(res => setTimeout(res, ms));
            while (document.querySelector('.btn-cargar-mas')) {
                const btn = document.querySelector('.btn-cargar-mas');
                btn.scrollIntoView();
                btn.click();
                await sleep(2000); // Esperar que carguen los nuevos
            }
        }
        """

        # 3. Configuración de ejecución
        run_config = CrawlerRunConfig(
            js_code=js_load_all,
            wait_for=".card-programas", # Espera que al menos uno exista
            magic_mode=True,
            cache_mode=CacheMode.BYPASS
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url="https://www.corfo.gob.cl/sites/cpp/programasyconvocatorias/",
                config=run_config
            )
            
            if result.success:
                # Aquí puedes elegir devolver markdown o procesar la lista
                # Si quieres los títulos limpios:
                return result.markdown.split('\n######')
            else:
                print(f"Error en scraping: {result.error_message}")
                return []