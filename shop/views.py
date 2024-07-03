from django.shortcuts import render

from rest_framework.response import Response

from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,DestroyAPIView,UpdateAPIView

from shop.serializers import UserSerializer

from django.contrib.auth.models import User

from shop.models import Product,Size,BasketItem,Order

from shop.serializers import ProductSerializer,BasketItemSerializer,BasketSerializer,OrderSerializer

from rest_framework import authentication,permissions

from rest_framework.viewsets import ViewSet

from rest_framework.views import APIView

from rest_framework import status

import razorpay



KEY_ID="rzp_test_bERsTXMGyCsika"

KEY_SECRET="gK9lZZ1F2HqaJh5V8X9xY9iY"



class SignUpView(CreateAPIView):

    serializer_class = UserSerializer

    queryset = User.objects.all()



class ProductListView(ListAPIView):

    serializer_class = ProductSerializer

    queryset = Product.objects.all()

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated]


 
class ProductDetilView(RetrieveAPIView):

    serializer_class = ProductSerializer

    queryset = Product.objects.all()

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated]



class AddToCartView(APIView):

    authentication_classes = [authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated]


    def post(self,request,*args,**kwargs):

        basket_obj = request.user.cart

        id = kwargs.get("pk")

        product_obj = Product.objects.get(id=id)

        size_name = request.data.get("size")

        quantity = request.data.get("quantity")

        size_obj = Size.objects.get(name=size_name)

        BasketItem.objects.create(

            basket_object=basket_obj,

            product_object=product_obj,

            size_object=size_obj,

            quantity=quantity
        )

        return Response(data={"message":"created"})


class AddToCartView(APIView):


    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,*args,**kwargs):

        basket_object=request.user.cart

        id=kwargs.get("pk")

        product_object=Product.objects.get(id=id)

        size_name=request.data.get("size")

        size_object=Size.objects.get(name=size_name)

        quantity=request.data.get("quantity")

        BasketItem.objects.create(
                                        basket_object=basket_object,

                                        product_object=product_object,

                                        size_object=size_object,

                                        quantity=quantity


                                          )
        return Response(data={"message":"created"})
    
    

class CartListView(APIView):


    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def get(self,request,*args,**kwargs):

        qs=request.user.cart

        serializer_instance=BasketSerializer(qs)

        return Response(data=serializer_instance.data)
    


class CartItemUpdateView(UpdateAPIView,DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    serializer_class=BasketItemSerializer

    queryset=BasketItem.objects.all()

    def perform_update(self,serializer):

        size_name=self.request.data.get("size_object")

        size_obj=Size.objects.get(name=size_name)

        serializer.save(size_object=size_obj)



class Checkout(APIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,*args,**kwargs):

        user_object=request.user

        delivery_address=request.data.get("delivery_address")

        phone=request.data.get("phone")

        pin=request.data.get("pin")

        email=request.data.get("email")

        payment_mode=request.data.get("payment_mode")

        order_instance=Order.objects.create(
                                user_object=user_object,

                                delivery_address=delivery_address,

                                phone=phone,

                                pin=pin,

                                email=email,
                                
                                payment_mode=payment_mode


                                )
        cart_items=request.user.cart.basketitems

        for bi in cart_items:

            order_instance.basket_item_objects.add(bi)

            bi.is_order_placed=True

            bi.save

        if payment_mode == "cod":

            order_instance.save()

            return Response(data={"message":"created"})

        elif payment_mode == "online" and order_instance:

            client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

            data = { "amount": order_instance.order_total*100, "currency": "INR", "receipt": "order_rcptid_11" }

            payment = client.order.create(data=data)

            print(payment)

            order_id=payment.get("id")

            key_id=KEY_ID

            order_total=payment.get("payment")

            user=request.user.username

            data={
                "order_id":order_id,
                "key_id":key_id,
                "order_total":order_total,
                "user":user,
                "phone":phone
            }

            order_instance.order_id =order_id

            order_instance.save()

            return Response(data=data,status=status.HTTP_201_CREATED)

        

class OrderSummaryView(ListAPIView):

     authentication_classes=[authentication.TokenAuthentication]

     permission_classes=[permissions.IsAuthenticated]

     serializer_class = OrderSerializer

     queryset = Order.objects.all() 


     def get_queryset(self):
         
         return Order.objects.filter(user_object=self.request.user)


class PyamentVerification(APIView):

    def post(self,request,*args,**kwargs):

        data = request.data

        client = razorpay.client(auth=(KEY_ID,KEY_SECRET))

        try:

            client.utility.verify_payment_signature(data)

            order_id = data.get('razorpay_order_id')

            order_obj = Order.objects.get(order_id=order_id)

            order_obj.is_paid = True

            order_obj.save()

            return Response(data={"message":"payment success"},status=status.HTTP_200_OK)

        except:

            return Response(data={"message":"payment failed"},status=status.HTTP_400_BAD_REQUEST)






    