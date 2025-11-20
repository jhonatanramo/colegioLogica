from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Parrafo, Repertorio
from ..serializers import ParrafoSerializer

# -------------------------------------------------------
# Obtener todos los párrafos
# -------------------------------------------------------
@api_view(['GET'])
def obtener_parrafos_todos(request):
    parrafos = Parrafo.objects.all()
    if not parrafos.exists():
        return Response({"error": "No hay párrafos"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ParrafoSerializer(parrafos, many=True)
    return Response(serializer.data)

# -------------------------------------------------------
# Crear uno o varios párrafos
# -------------------------------------------------------
@api_view(['POST'])
def crear_parrafo(request):

    parrafo_texto = request.data.get('parrafo')
    repertorio_id = request.data.get('id_repertorio')
    if not parrafo_texto or not repertorio_id:
        return Response({"error": "Faltan datos", "recibido": request.data}, status=status.HTTP_400_BAD_REQUEST)
    try:
        repertorio = Repertorio.objects.get(id=repertorio_id)
    except Repertorio.DoesNotExist:
        return Response({"error": "Repertorio no existe"}, status=status.HTTP_400_BAD_REQUEST)

    # Si viene texto con --- los separamos, si no, lo tratamos como único
    if "---" in parrafo_texto:
        listas = [p.strip() for p in parrafo_texto.split("---") if p.strip()]
    else:
        listas = [parrafo_texto.strip()]

    parrafos_creados = []
    for index, texto in enumerate(listas):
        # Asignar orden automáticamente
        data = {
            "parrafo": texto, 
            "repertorio": repertorio.id,
        }
        
        serializer = ParrafoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            parrafos_creados.append(serializer.data)
        else:
            print("❌ Error serializer:", serializer.errors)
            return Response({"error_serializer": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"mensaje": "Párrafos creados exitosamente", "parrafos": parrafos_creados},
        status=status.HTTP_201_CREATED
    )
# -------------------------------------------------------
# Obtener párrafos por repertorio
# -------------------------------------------------------
@api_view(['GET'])
def obtener_parrafos(request, nro):
    parrafos = Parrafo.objects.filter(repertorio=nro).order_by('id')

    if not parrafos.exists():
        return Response({"error": "Parrafo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ParrafoSerializer(parrafos, many=True)
    return Response(serializer.data)

# -------------------------------------------------------
# Eliminar todos los párrafos de un repertorio
# -------------------------------------------------------
@api_view(['DELETE'])
def eliminar_parrafo(request):
    id_Repertorio = request.GET.get('id')
    if not id_Repertorio:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        parrafos = Parrafo.objects.filter(repertorio=id_Repertorio)
        cantidad = parrafos.count()
        if cantidad == 0:
            return Response({"error": "No hay párrafos para eliminar"}, status=status.HTTP_404_NOT_FOUND)
        parrafos.delete()
        return Response({"mensaje": f"{cantidad} párrafos eliminados exitosamente"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
