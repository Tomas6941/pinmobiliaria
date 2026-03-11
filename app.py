from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import json, os

app = Flask(__name__)
app.secret_key = 'inmobiliaria_prime_2024'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    default = {
        'propiedades': [],
        'consultas': [],
        'config': {
            'nombre': 'Prime Inmobiliaria',
            'slogan': 'Tu propiedad ideal, a un paso.',
            'telefono': '(011) 4567-8900',
            'email': 'ventas@primeinmobiliaria.com.ar',
            'direccion': 'Av. Santa Fe 3421, Piso 3, CABA'
        }
    }
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for k, v in default.items():
                if k not in data:
                    data[k] = v
            return data
    return default

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    data = load_data()
    props = [p for p in data['propiedades'] if p.get('activa', True)]
    destacadas = [p for p in props if p.get('destacada')][:6]
    return render_template('index.html', config=data['config'], destacadas=destacadas)

@app.route('/propiedades')
def propiedades():
    data = load_data()
    props = [p for p in data['propiedades'] if p.get('activa', True)]
    operacion = request.args.get('operacion', '')
    tipo = request.args.get('tipo', '')
    zona = request.args.get('zona', '')
    precio_max = request.args.get('precio_max', '')
    if operacion:
        props = [p for p in props if p.get('operacion') == operacion]
    if tipo:
        props = [p for p in props if p.get('tipo') == tipo]
    if zona:
        props = [p for p in props if zona.lower() in p.get('zona', '').lower()]
    if precio_max:
        try:
            props = [p for p in props if float(p.get('precio', 0)) <= float(precio_max)]
        except ValueError:
            pass
    zonas = sorted(set(p.get('zona', '') for p in [p for p in data['propiedades'] if p.get('activa', True)] if p.get('zona')))
    return render_template('propiedades.html', config=data['config'],
                           propiedades=props, zonas=zonas, filtros=request.args)

@app.route('/propiedad/<int:pid>')
def propiedad_detalle(pid):
    data = load_data()
    prop = next((p for p in data['propiedades'] if p.get('id') == pid), None)
    if not prop or not prop.get('activa', True):
        return redirect(url_for('propiedades'))
    relacionadas = [p for p in data['propiedades']
                    if p.get('activa', True) and p.get('tipo') == prop.get('tipo')
                    and p.get('id') != pid][:3]
    return render_template('propiedad_detalle.html', config=data['config'],
                           prop=prop, relacionadas=relacionadas)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    data = load_data()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        interes = request.form.get('interes', '')
        mensaje = request.form.get('mensaje', '').strip()
        if nombre and email and mensaje:
            data['consultas'].append({
                'id': len(data['consultas']) + 1,
                'nombre': nombre, 'email': email,
                'telefono': telefono, 'interes': interes,
                'mensaje': mensaje
            })
            save_data(data)
            flash('¡Consulta recibida! Un asesor te contactará en menos de 24 hs.', 'success')
            return redirect(url_for('contacto'))
        flash('Completá todos los campos requeridos.', 'error')
    return render_template('contacto.html', config=data['config'])

@app.route('/nosotros')
def nosotros():
    data = load_data()
    return render_template('nosotros.html', config=data['config'])

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('usuario') == 'admin' and request.form.get('password') == 'prime2024':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        flash('Credenciales incorrectas.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_panel():
    data = load_data()
    props = data['propiedades']
    stats = {
        'total': len([p for p in props if p.get('activa', True)]),
        'venta': len([p for p in props if p.get('operacion') == 'venta' and p.get('activa', True)]),
        'alquiler': len([p for p in props if p.get('operacion') == 'alquiler' and p.get('activa', True)]),
        'consultas': len(data['consultas'])
    }
    return render_template('admin.html', config=data['config'], propiedades=props,
                           consultas=data['consultas'][-10:], stats=stats)

@app.route('/admin/propiedad/nueva', methods=['GET', 'POST'])
@login_required
def admin_prop_nueva():
    if request.method == 'POST':
        data = load_data()
        nueva_id = max((p.get('id', 0) for p in data['propiedades']), default=0) + 1
        prop = {
            'id': nueva_id,
            'titulo': request.form.get('titulo', ''),
            'operacion': request.form.get('operacion', 'venta'),
            'tipo': request.form.get('tipo', 'departamento'),
            'precio': request.form.get('precio', ''),
            'moneda': request.form.get('moneda', 'USD'),
            'zona': request.form.get('zona', ''),
            'direccion': request.form.get('direccion', ''),
            'ambientes': request.form.get('ambientes', ''),
            'dormitorios': request.form.get('dormitorios', ''),
            'banos': request.form.get('banos', ''),
            'superficie_total': request.form.get('superficie_total', ''),
            'superficie_cubierta': request.form.get('superficie_cubierta', ''),
            'descripcion': request.form.get('descripcion', ''),
            'imagen_url': request.form.get('imagen_url', ''),
            'destacada': bool(request.form.get('destacada')),
            'activa': bool(request.form.get('activa', True))
        }
        data['propiedades'].append(prop)
        save_data(data)
        flash('Propiedad publicada correctamente.', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('admin_prop_form.html', prop=None)

@app.route('/admin/propiedad/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def admin_prop_editar(pid):
    data = load_data()
    prop = next((p for p in data['propiedades'] if p.get('id') == pid), None)
    if not prop:
        return redirect(url_for('admin_panel'))
    if request.method == 'POST':
        prop.update({
            'titulo': request.form.get('titulo', ''),
            'operacion': request.form.get('operacion', 'venta'),
            'tipo': request.form.get('tipo', 'departamento'),
            'precio': request.form.get('precio', ''),
            'moneda': request.form.get('moneda', 'USD'),
            'zona': request.form.get('zona', ''),
            'direccion': request.form.get('direccion', ''),
            'ambientes': request.form.get('ambientes', ''),
            'dormitorios': request.form.get('dormitorios', ''),
            'banos': request.form.get('banos', ''),
            'superficie_total': request.form.get('superficie_total', ''),
            'superficie_cubierta': request.form.get('superficie_cubierta', ''),
            'descripcion': request.form.get('descripcion', ''),
            'imagen_url': request.form.get('imagen_url', ''),
            'destacada': bool(request.form.get('destacada')),
            'activa': bool(request.form.get('activa'))
        })
        save_data(data)
        flash('Propiedad actualizada.', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('admin_prop_form.html', prop=prop)

@app.route('/admin/propiedad/eliminar/<int:pid>', methods=['POST'])
@login_required
def admin_prop_eliminar(pid):
    data = load_data()
    for p in data['propiedades']:
        if p.get('id') == pid:
            p['activa'] = False
            break
    save_data(data)
    flash('Propiedad dada de baja.', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
