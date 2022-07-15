import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from sync_functions.py import Stock, Trading_info

# Create a GraphQL type for the actor model
class StockType(DjangoObjectType):
    class Meta:
        model = Stock

# Create a GraphQL type for the movie model
class Trading_infoType(DjangoObjectType):
    class Meta:
        model = Trading_infoType



# Create a Query type
class Query(ObjectType):
    Stock = graphene.Field(Stock, id=graphene.Int())
    Trading_info = graphene.Field(Trading_info, id=graphene.Int())
    Stock = graphene.List(StockType)
    Trading_info= graphene.List(Trading_infoType)

    def resolve_stock(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return stock.objects.get(pk=id)

        return None

    def resolve_Trading_info(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Trading_infoType.objects.get(pk=id)

        return None

    def resolve_Stock(self, info, **kwargs):
        return Stock.objects.all()

    def resolve_Trading_Stock(self, info, **kwargs):
        return Movie.objects.all()