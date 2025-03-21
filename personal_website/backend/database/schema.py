"""
Database schema initialization for the personal website.
Sets up initial database with sample data.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from database.models import db, User, Category, Tag, Article, Comment, Setting, Media

def init_database(app):
    """
    Initialize the database with sample data.
    
    Args:
        app: Flask application with database context
    """
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user
        create_admin_user()
        
        # Create sample categories
        create_categories()
        
        # Create sample tags
        create_tags()
        
        # Create sample articles
        create_articles()
        
        # Create sample comments
        create_comments()
        
        # Create default settings
        create_settings()
        
        # Commit all changes
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            app.logger.error("Error initializing database. Some records might already exist.")

def create_admin_user():
    """Create a default admin user if none exists."""
    if User.query.filter_by(email='admin@example.com').first() is None:
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_password_hash('Admin@123'),
            role='admin',
            bio='Website administrator',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # Create a contributor user as well
        contributor = User(
            name='Contributor User',
            email='contributor@example.com',
            password=generate_password_hash('Contributor@123'),
            role='contributor',
            bio='Regular content contributor',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(contributor)
        
        # Create a regular viewer user
        viewer = User(
            name='Viewer User',
            email='viewer@example.com',
            password=generate_password_hash('Viewer@123'),
            role='viewer',
            bio='Regular website visitor',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(viewer)

def create_categories():
    """Create sample article categories."""
    categories = [
        {
            'name': 'Technology',
            'description': 'Articles related to technology, programming, and software development.'
        },
        {
            'name': 'Personal',
            'description': 'Personal thoughts, experiences, and reflections.'
        },
        {
            'name': 'Tutorials',
            'description': 'Step-by-step guides and tutorials on various topics.'
        },
        {
            'name': 'Projects',
            'description': 'Information about my personal and professional projects.'
        },
        {
            'name': 'Reviews',
            'description': 'Reviews of books, tools, and technologies.'
        }
    ]
    
    for category_data in categories:
        if Category.query.filter_by(name=category_data['name']).first() is None:
            category = Category(
                name=category_data['name'],
                description=category_data['description']
            )
            db.session.add(category)

def create_tags():
    """Create sample article tags."""
    tags = [
        'Python', 'JavaScript', 'Web Development', 'Flask', 'React',
        'Database', 'API', 'Backend', 'Frontend', 'DevOps',
        'Cloud', 'Docker', 'Git', 'Machine Learning', 'UI/UX',
        'Career', 'Productivity', 'Learning', 'Best Practices', 'Tools'
    ]
    
    for tag_name in tags:
        if Tag.query.filter_by(name=tag_name).first() is None:
            tag = Tag(name=tag_name)
            db.session.add(tag)

def create_articles():
    """Create sample articles."""
    # Get users
    admin = User.query.filter_by(email='admin@example.com').first()
    contributor = User.query.filter_by(email='contributor@example.com').first()
    
    if not admin or not contributor:
        return
    
    # Get categories
    tech_category = Category.query.filter_by(name='Technology').first()
    tutorial_category = Category.query.filter_by(name='Tutorials').first()
    personal_category = Category.query.filter_by(name='Personal').first()
    
    if not tech_category or not tutorial_category or not personal_category:
        return
    
    # Get tags
    python_tag = Tag.query.filter_by(name='Python').first()
    javascript_tag = Tag.query.filter_by(name='JavaScript').first()
    flask_tag = Tag.query.filter_by(name='Flask').first()
    react_tag = Tag.query.filter_by(name='React').first()
    web_dev_tag = Tag.query.filter_by(name='Web Development').first()
    
    if not python_tag or not javascript_tag or not flask_tag or not react_tag or not web_dev_tag:
        return
    
    # Create sample articles
    articles = [
        {
            'title': 'Getting Started with Flask',
            'content': """
# Getting Started with Flask

Flask is a lightweight web framework for Python. It's designed to make getting started quick and easy, with the ability to scale up to complex applications.

## Installation

You can install Flask using pip:

```python
pip install flask
```

## Hello World Example

Here's a simple Hello World application using Flask:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

Save this code in a file named `app.py` and run it:

```bash
python app.py
```

Then, open your browser and go to `http://localhost:5000/`. You should see "Hello, World!" displayed.

## Basic Routing

Flask uses decorators to map URLs to functions:

```python
@app.route('/about')
def about():
    return 'About page'

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User: {username}'
```

## Templates

Flask uses Jinja2 as its template engine. Here's a simple example:

```python
from flask import render_template

@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)
```

And in `templates/hello.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello</title>
</head>
<body>
    <h1>Hello, {{ name }}!</h1>
</body>
</html>
```

## Conclusion

Flask is a great choice for building web applications in Python, especially when you want something lightweight and flexible. This tutorial just scratches the surface of what you can do with Flask.
            """,
            'excerpt': 'A beginner-friendly introduction to the Flask web framework for Python. Learn the basics of setting up a Flask application with examples.',
            'status': 'published',
            'is_featured': True,
            'author': admin,
            'category': tutorial_category,
            'tags': [python_tag, flask_tag, web_dev_tag],
            'published_at': datetime.utcnow()
        },
        {
            'title': 'Building a React Frontend',
            'content': """
# Building a React Frontend

React is a JavaScript library for building user interfaces. It's maintained by Facebook and a community of individual developers and companies.

## Setting Up a React Project

The easiest way to create a React project is to use Create React App:

```bash
npx create-react-app my-app
cd my-app
npm start
```

This will create a new React project and start a development server.

## Components

Components are the building blocks of any React application. Here's a simple component:

```jsx
import React from 'react';

function HelloWorld() {
  return <h1>Hello, World!</h1>;
}

export default HelloWorld;
```

## State and Props

React components can have state and receive props:

```jsx
import React, { useState } from 'react';

function Counter(props) {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>{props.title}</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}

export default Counter;
```

## Hooks

Hooks are a new addition in React 16.8 that allow you to use state and other React features without writing a class:

```jsx
import React, { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    document.title = `You clicked ${count} times`;
  }, [count]);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## Conclusion

React is a powerful library for building modern web applications. With its component-based architecture and virtual DOM, it's an efficient way to build user interfaces.
            """,
            'excerpt': 'Learn how to create a modern and responsive frontend using React. This article covers React components, state management, and more.',
            'status': 'published',
            'is_featured': True,
            'author': contributor,
            'category': tech_category,
            'tags': [javascript_tag, react_tag, web_dev_tag],
            'published_at': datetime.utcnow()
        },
        {
            'title': 'My Journey as a Developer',
            'content': """
# My Journey as a Developer

Everyone's journey into the world of programming is different. Here's my story and the lessons I've learned along the way.

## The Beginning

I first became interested in programming when I was in high school. I was always fascinated by computers and how they worked. When I discovered that I could create my own programs, I was hooked.

My first language was Python. I loved how readable and intuitive it was. I started with simple console applications and gradually worked my way up to more complex projects.

## College Years

In college, I expanded my horizons by learning other languages like Java, C++, and JavaScript. I also took courses in algorithms, data structures, and software engineering principles.

During this time, I worked on several team projects that taught me the importance of collaboration, version control, and clean code. I also did a few internships that gave me real-world experience.

## Professional Career

After college, I landed a job as a junior developer at a tech startup. It was challenging but incredibly rewarding. I learned so much about building production-quality software, working in an agile environment, and dealing with real-world constraints.

Over the years, I've worked on a variety of projects, from web applications to mobile apps to back-end systems. Each project has taught me something new and has helped me grow as a developer.

## Continuous Learning

One of the things I love about being a developer is that there's always something new to learn. The tech industry moves quickly, and staying current requires continuous learning and adaptation.

I try to dedicate some time each week to learning new technologies or improving my skills. Whether it's through online courses, books, or side projects, continuous learning is essential for growth.

## Advice for Aspiring Developers

If you're just starting your journey as a developer, here are a few pieces of advice:

1. **Start with the basics**: Make sure you have a solid understanding of programming fundamentals before diving into frameworks and libraries.

2. **Build projects**: Theory is important, but there's no substitute for hands-on experience. Build projects that interest you.

3. **Embrace challenges**: Don't shy away from difficult problems. They're opportunities for growth.

4. **Learn to collaborate**: Programming is often a team effort. Learn to work effectively with others and to use tools like Git.

5. **Be patient**: Becoming a good developer takes time. Don't get discouraged if things don't click immediately.

## Conclusion

Being a developer has been a rewarding journey for me. It's a career that offers continuous growth, intellectual challenges, and the satisfaction of creating something useful. If you're considering this path, I encourage you to take the first step and see where it leads you.
            """,
            'excerpt': 'A personal reflection on my journey as a software developer, from early beginnings to professional growth, with advice for those starting out.',
            'status': 'published',
            'is_featured': False,
            'author': admin,
            'category': personal_category,
            'tags': [],
            'published_at': datetime.utcnow()
        }
    ]
    
    for article_data in articles:
        # Check if article with same title exists
        if Article.query.filter_by(title=article_data['title']).first() is None:
            article = Article(
                title=article_data['title'],
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                status=article_data['status'],
                is_featured=article_data['is_featured'],
                author=article_data['author'],
                category=article_data['category'],
                published_at=article_data['published_at'],
                created_at=datetime.utcnow()
            )
            
            # Add tags to article
            for tag in article_data['tags']:
                article.tags.append(tag)
            
            db.session.add(article)

def create_comments():
    """Create sample comments on articles."""
    # Get users
    admin = User.query.filter_by(email='admin@example.com').first()
    contributor = User.query.filter_by(email='contributor@example.com').first()
    viewer = User.query.filter_by(email='viewer@example.com').first()
    
    if not admin or not contributor or not viewer:
        return
    
    # Get articles
    flask_article = Article.query.filter_by(title='Getting Started with Flask').first()
    react_article = Article.query.filter_by(title='Building a React Frontend').first()
    
    if not flask_article or not react_article:
        return
    
    # Create sample comments
    comments = [
        {
            'content': 'Great tutorial! This helped me understand Flask better.',
            'user': viewer,
            'article': flask_article,
            'is_approved': True,
            'created_at': datetime.utcnow()
        },
        {
            'content': 'Could you expand on the template section? I would like to see more examples.',
            'user': contributor,
            'article': flask_article,
            'is_approved': True,
            'created_at': datetime.utcnow()
        },
        {
            'content': 'Thanks for the feedback! I will add more examples in a future update.',
            'user': admin,
            'article': flask_article,
            'is_approved': True,
            'created_at': datetime.utcnow()
        },
        {
            'content': 'This React tutorial is exactly what I needed. Clear and concise!',
            'user': viewer,
            'article': react_article,
            'is_approved': True,
            'created_at': datetime.utcnow()
        },
        {
            'content': 'Have you considered covering React Router in a future article?',
            'user': admin,
            'article': react_article,
            'is_approved': True,
            'created_at': datetime.utcnow()
        }
    ]
    
    for comment_data in comments:
        comment = Comment(
            content=comment_data['content'],
            user=comment_data['user'],
            article=comment_data['article'],
            is_approved=comment_data['is_approved'],
            created_at=comment_data['created_at']
        )
        db.session.add(comment)

def create_settings():
    """Create default website settings."""
    settings = [
        {
            'name': 'site_title',
            'value': 'My Personal Website',
            'description': 'The title of the website'
        },
        {
            'name': 'site_description',
            'value': 'A personal website for sharing knowledge and experiences',
            'description': 'A short description of the website'
        },
        {
            'name': 'posts_per_page',
            'value': '10',
            'description': 'Number of posts to display per page'
        },
        {
            'name': 'enable_comments',
            'value': 'true',
            'description': 'Enable or disable comments on articles'
        },
        {
            'name': 'moderated_comments',
            'value': 'false',
            'description': 'Require comment approval before publishing'
        },
        {
            'name': 'github_url',
            'value': 'https://github.com/yourusername',
            'description': 'Your GitHub profile URL'
        },
        {
            'name': 'linkedin_url',
            'value': 'https://linkedin.com/in/yourusername',
            'description': 'Your LinkedIn profile URL'
        },
        {
            'name': 'twitter_url',
            'value': 'https://twitter.com/yourusername',
            'description': 'Your Twitter profile URL'
        }
    ]
    
    for setting_data in settings:
        if Setting.query.filter_by(name=setting_data['name']).first() is None:
            setting = Setting(
                name=setting_data['name'],
                value=setting_data['value'],
                description=setting_data['description']
            )
            db.session.add(setting)