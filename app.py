from init import create_app, create_database

if __name__ == "__main__":
   app = create_app()
   app.run(debug=True)
   #app.run(host="192.168.1.160",port=5500)

#app = create_app()
#ptcreate_database(app)

#init.pt

