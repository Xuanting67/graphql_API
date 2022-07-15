import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from sync_functions.py import Stock, Trading_info

# Create a GraphQL type for the stock model
class StockType(DjangoObjectType):
    class Meta:
        model = Stock

# Create a GraphQL type for the trading info model
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
        return Trading_infoType.objects.all()


# Create Input Object Types
class StockInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()

class Trading_infoInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    stock = graphene.List(ActorInput)
    year = graphene.Int()

# Create mutations for stocks
class CreateActor(graphene.Mutation):
    class Arguments:
        input = StockInput(required=True)

    ok = graphene.Boolean()
    Stock = graphene.Field(StockType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        Stock_instance = stock(name=input.name)
        Stock_instance.save()
        return CreateStock(ok=ok, actor=Stock_instance)

class UpdateStock(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = StockInput(required=True)

    ok = graphene.Boolean()
    Stock = graphene.Field(StockType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        Stock_instance = Stock.objects.get(pk=id)
        if Stock_instance:
            ok = True
            Stock.name = input.name
            Stock.save()
            return UpdateStock(ok=ok, stock=Stock_instance)
        return UpdateStock(ok=ok, stock=None)