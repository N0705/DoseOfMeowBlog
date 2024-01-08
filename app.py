from init import create_app, create_database

if __name__ == "__main__":
   app = create_app()
   app.run(debug=True)

#app = create_app()
#ptcreate_database(app)


#init.py