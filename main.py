class generate_reports():
    def __init__(self) -> None:
        self.prepare()
        self.read_data()
        #self.print_report()
        self.print_all()
    
    def prepare(self):
        import pandas
        self.pandas=pandas

        from PDF_report.LIB_MYREPORT import pdf_printer
        self.pdf_printer=pdf_printer
        
    def read_data(self):
        #read data
        self.data=self.pandas.read_csv('./sales_data.csv')
        #filter a day
        self.data['Order Date']=self.pandas.to_datetime(self.data['Order Date'])
        self.data['Date']=self.data['Order Date'].dt.date.map(lambda x:str(x))
        self.day='2019-01-22' #choose a day
        self.data=self.data[self.data['Date']==self.day]
        self.data['street']=self.data['Purchase Address'].map(lambda x:x.split(',')).str.get(0)
        self.data['city']=self.data['Purchase Address'].map(lambda x:x.split(',')).str.get(1)
        self.data['state']=self.data['Purchase Address'].map(lambda x:x.split(',')).str.get(2)

        #create a function to insert columns using random
        def random_colum(list,col_name='column'):
            import random
            orders=self.pandas.DataFrame(self.data['Order ID'].unique(),columns=['order_ID'])
            orders[col_name]=orders.index.map(lambda x: random.sample(list,1)[0])
            orders.set_index('order_ID',inplace=True)
            self.data=self.pandas.merge(left=self.data,right=orders,left_on='Order ID',right_index=True,how='left')
        #insert a column to identify the salesman
        salesman=[101,102,103,104,105,201,202,203,204,205]
        random_colum(list=salesman,col_name='salesman')
        #insert a column with the order status
        order_status=['ok','ok','ok','ok','ok','ok','ok','ok','ok','canceled']
        random_colum(list=order_status,col_name='status')

    def print_report(self,salesman=101):
        from PDF_report.LIB_MYREPORT import pdf_printer
        import datetime
        time=datetime.datetime.now()

        #format data
        orders=self.data[self.data['salesman']==salesman]

        def formating(df):
            for col in ['turnover']:
                df[col]=df[col].map(lambda x:round(x,2)).map(lambda x:'$'+str(x))
            return df
        
        
        #start the report
        path=f'./REPORTS/daily_report_{salesman}.pdf'
        document=pdf_printer(path=path,
                            main_header=f'DAILY REPORT - {self.day}',
                            sub_header=f'Salesman {salesman}',
                            footer='updated: '+str(time))
        
        #first page
        def print_orders():
            document.insert_paragraph(text='ORDERS',style='title1')
            
            for i,order in enumerate(orders['Order ID'].unique()):
                df_order=orders[orders['Order ID']==order]

                address=df_order.loc[:,'Purchase Address'].unique()[0]
                document.insert_paragraph(text=f'CLIENT {i} ---  Address: {address}',style='title2')

                order_num=df_order.loc[:,'Order ID'].unique()[0]
                document.insert_paragraph(text=f'Order number: {order_num}',style='normal',spacer=False)

                status=df_order.loc[:,'status'].unique()[0]
                document.insert_paragraph(text=f'Status: {status}',style='normal',spacer=False)
                columns=['Product_ean','Product','Quantity Ordered','Price Each','turnover']
                document.insert_table(dataframe=df_order[columns],style='green')
                document.insert_spacer()
        print_orders()

        document.jump_page()

        #second page
        def print_list_orders():
            document.insert_paragraph(text='SUMMARY - SALES ORDERS',style='title1')

            order_list=orders.groupby(['city','Order ID','status'])[['turnover']].sum().reset_index()
            order_list=formating(order_list)
            document.insert_table(dataframe=order_list)
        print_list_orders()

        document.jump_page()

        #third page
        def print_results_summary():
            document.insert_paragraph(text='SUMMARY RESULTS',style='title1')

            document.insert_paragraph(text=f'SUMMARY ITENS',style='title2')
            summary_itens=orders.groupby(['catégorie','Product'])[['Quantity Ordered','turnover']].sum().reset_index()
            summary_itens=formating(summary_itens)
            document.insert_table(dataframe=summary_itens)

            document.insert_paragraph(text=f'SUMMARY CATEGORIE',style='title2')
            summary_categorie=orders.groupby(['catégorie'])[['Quantity Ordered','turnover']].sum().reset_index()
            summary_categorie=formating(df=summary_categorie)
            document.insert_table(dataframe=summary_categorie)

            turnover=orders['turnover'].sum()
            document.insert_paragraph(text=f'TOTAL: ${round(turnover,2)}')


        print_results_summary()

        document.save_document(path='')

    def print_all(self):
        for i in sorted(self.data['salesman'].unique()):
            self.print_report(salesman=i)
            print('-report printed, salesman:',i)


        
generate_reports()