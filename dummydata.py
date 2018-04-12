#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Country, Base, Project, User

engine = create_engine('sqlite:///projectmanagement.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Create dummy user

User1 = User(name='Chandraveer Singh',
             email='chandraveersinghrajawat@gmail.com',
             picture='https://png.pngtree.com/element_pic/17/07/23/3e1a80864fe450b9312f5cb7cf486dcf.jpg'
             )
session.add(User1)
session.commit()

# Projects in India

country1 = Country(user_id=1, name='India')

session.add(country1)
session.commit()

project1 = Project(
    user_id=1,
    name='Project1',
    description='this is a hrm project',
    number_of_members='60',
    category='HRMProject',
    country=country1,
    )

session.add(project1)
session.commit()

project2 = Project(
    user_id=1,
    name='Project2',
    description='this is a fin project',
    number_of_members='100',
    category='FINProject',
    country=country1,
    )

session.add(project2)
session.commit()

project3 = Project(
    user_id=1,
    name='Project3',
    description='this is a analytics project',
    number_of_members='50',
    category='ANALYTICSProject',
    country=country1,
    )

session.add(project3)
session.commit()

# Projects in USA

country2 = Country(user_id=1, name='USA')

session.add(country2)
session.commit()

project1 = Project(
    user_id=1,
    name='Project1',
    description='this is a hrm project',
    number_of_members='60',
    category='HRMProject',
    country=country2,
    )

session.add(project1)
session.commit()

project2 = Project(
    user_id=1,
    name='Project2',
    description='this is a fin project',
    number_of_members='100',
    category='FINProject',
    country=country2,
    )

session.add(project2)
session.commit()

project3 = Project(
    user_id=1,
    name='Project3',
    description='this is a analytics project',
    number_of_members='50',
    category='ANALYTICSProject',
    country=country2,
    )

session.add(project3)
session.commit()

# Projects in Australia

country3 = Country(user_id=1, name='Australia')

session.add(country3)
session.commit()

project1 = Project(
    user_id=1,
    name='Project1',
    description='this is a hrm project',
    number_of_members='60',
    category='HRMProject',
    country=country3,
    )

session.add(project1)
session.commit()

project2 = Project(
    user_id=1,
    name='Project2',
    description='this is a fin project',
    number_of_members='100',
    category='FINProject',
    country=country3,
    )

session.add(project2)
session.commit()

project3 = Project(
    user_id=1,
    name='Project3',
    description='this is a analytics project',
    number_of_members='50',
    category='ANALYTICSProject',
    country=country3,
    )

session.add(project3)
session.commit()

# Projects in Japan

country4 = Country(user_id=1, name='Japan')

session.add(country4)
session.commit()

project1 = Project(
    user_id=1,
    name='Project1',
    description='this is a hrm project',
    number_of_members='60',
    category='HRMProject',
    country=country4,
    )

session.add(project1)
session.commit()

project2 = Project(
    user_id=1,
    name='Project2',
    description='this is a fin project',
    number_of_members='100',
    category='FINProject',
    country=country4,
    )

session.add(project2)
session.commit()

project3 = Project(
    user_id=1,
    name='Project3',
    description='this is a analytics project',
    number_of_members='50',
    category='ANALYTICSProject',
    country=country4,
    )

session.add(project3)
session.commit()

# Projects in Germany

country5 = Country(user_id=1, name='Germany')

session.add(country5)
session.commit()

project1 = Project(
    user_id=1,
    name='Project1',
    description='this is a hrm project',
    number_of_members='60',
    category='HRMProject',
    country=country5,
    )

session.add(project1)
session.commit()

project2 = Project(
    user_id=1,
    name='Project2',
    description='this is a fin project',
    number_of_members='100',
    category='FINProject',
    country=country5,
    )

session.add(project2)
session.commit()

project3 = Project(
    user_id=1,
    name='Project3',
    description='this is a analytics project',
    number_of_members='50',
    category='ANALYTICSProject',
    country=country5,
    )

session.add(project3)
session.commit()

print 'added project items!'
