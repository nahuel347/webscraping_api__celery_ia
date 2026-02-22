"""
Views for the recipe APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
import asyncio
from asgiref.sync import async_to_sync
import httpx
import re
from rest_framework import viewsets
from rest_framework.response import Response
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Create your views here.
from core.models import Recipe, Tag, Ingredient
from recipe import serializers
import random

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='separacion por , para diferenciar los tags ',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='separacion por , para diferenciar los filter',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ViewSet):
    def list(self, request):
        data = async_to_sync(self._get_data)()
        print(data)
        return Response({"data": data, "total": len(data)})

    



    async def _get_data(self):
        browser_config = BrowserConfig(
            headless=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            },
            extra_args=["--disable-blink-features=AutomationControlled"]
        )
        
        all_programs = []
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for page_num in range(1, 7):
                print(f"--- 🚀 Procesando Página {page_num} ---")
                
                js_code = ""
                if page_num > 1:
                    # TRUCO: Vaciamos el contenido ANTES del clic. 
                    # Así el wait_for solo se cumplirá cuando lleguen datos NUEVOS.
                    js_code = f"""
                    (async () => {{
                        const targetPage = "{page_num}";
                        const container = document.querySelector('#_corfoportallists_WAR_corfoportallistsportlet_programasConvocatorias');
                        const buttons = Array.from(document.querySelectorAll('a.page-link'));
                        const btn = buttons.find(b => b.innerText.trim() === targetPage);
                        
                        if (btn) {{
                            if (container) container.innerHTML = ''; // Borrado físico de los items viejos
                            btn.scrollIntoView({{behavior: 'instant', block: 'center'}});
                            btn.click();
                            return true;
                        }}
                        return false;
                    }})();
                    """

                run_config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    js_code=js_code if page_num > 1 else None,
                    # La condición de espera ahora es doble: Página activa correcta Y que hayan vuelto a aparecer los items
                    wait_for=f"js:() => {{ \
                        const active = document.querySelector('li.page-item.active'); \
                        const items = document.querySelectorAll('.noticias-item-completo'); \
                        return active && active.innerText.trim() === '{page_num}' && items.length > 0; \
                    }}",
                    wait_until="networkidle",
                    page_timeout=18000 
                )

                result = await crawler.arun(
                    url="https://www.corfo.gob.cl/sites/cpp/programasyconvocatorias/",
                    config=run_config
                )

                if result.success:
                    # Pausa técnica para que el DOM termine de estabilizarse
                    #await asyncio.sleep(5)
                    
                    content = result.markdown
                    import re
                    links = re.findall(r'https://www.corfo.gob.cl/sites/cpp/convocatoria/[a-zA-Z0-9\-_]+', content)
                    
                    new_found = 0
                    for link in links:
                        clean_link = link.lower().strip().rstrip('/')
                        if clean_link not in all_programs:
                            all_programs.append(clean_link)
                            new_found += 1
                    
                    print(f"✅ Página {page_num}: +{new_found} nuevos. Total: {len(all_programs)}")
                    
                    # Si a pesar de todo no hay nuevos, intentamos un reintento rápido
                    if new_found == 0 and page_num > 1:
                        print(f"⚠️ Error de sincronía en pág {page_num}. Los datos no refrescaron.")
                else:
                    print(f"❌ Error: {result.error_message}")

                await asyncio.sleep(random.uniform(2, 4))

        return all_programs

    def get_serializer_class(self):

        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):

        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='filtro por item asignado a recipe.',
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

class TagViewSet(BaseRecipeAttrViewSet):

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()



class IngredientViewSet(BaseRecipeAttrViewSet):
  
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


