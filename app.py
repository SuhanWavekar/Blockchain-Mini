import hashlib
import json
import uuid
import time
import io
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, send_file, session
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
import qrcode.image.pil

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'blockchain-demo-secret-key-change-me')

BASE_DIR = Path(__file__).resolve().parent
CHAIN_FILE = BASE_DIR / 'blockchain.json'
DIFFICULTY = 2  # number of leading zeros for proof of work

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def current_time():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def calculate_hash(block):
    block_data = {
        'index': block['index'],
        'timestamp': block['timestamp'],
        'data': block['data'],
        'previous_hash': block['previous_hash']
    }
    if 'nonce' in block:
        block_data['nonce'] = block['nonce']
    
    encoded_block = json.dumps(block_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded_block).hexdigest()

class Blockchain:
    def __init__(self):
        self.difficulty = DIFFICULTY
        if CHAIN_FILE.exists():
            try:
                self.chain = json.loads(CHAIN_FILE.read_text(encoding='utf-8'))
                if not isinstance(self.chain, list) or not self.chain:
                    raise ValueError('Invalid')
            except (json.JSONDecodeError, ValueError):
                raise RuntimeError('blockchain.json is invalid. Remove it to start fresh.')
        else:
            self.chain = []
            self._create_genesis()
            self._save()

    def _create_genesis(self):
        block = {
            'index': 0,
            'timestamp': current_time(),
            'data': {'message': 'Genesis Block'},
            'previous_hash': '0',
            'nonce': 0,
        }
        self._mine(block)
        self.chain.append(block)

    def _mine(self, block):
        """Proof of work: find nonce so hash starts with '0' * difficulty."""
        target = '0' * self.difficulty
        start = time.time()
        nonce = 0
        while True:
            block['nonce'] = nonce
            h = calculate_hash(block)
            if h.startswith(target):
                block['hash'] = h
                block['mining_time'] = round(time.time() - start, 4)
                logger.info(f"Block {block['index']} mined: nonce={nonce}, time={block['mining_time']}s")
                return
            nonce += 1

    def _save(self):
        CHAIN_FILE.write_text(json.dumps(self.chain, indent=4), encoding='utf-8')

    def add_certificate(self, student_name, course, institution):
        certificate = {
            'certificate_id': str(uuid.uuid4()).upper(),
            'student_name': student_name,
            'course': course,
            'institution': institution,
            'issue_date': current_time(),
        }
        block = {
            'index': len(self.chain),
            'timestamp': current_time(),
            'data': certificate,
            'previous_hash': self.chain[-1]['hash'],
            'nonce': 0,
        }
        self._mine(block)
        self.chain.append(block)
        self._save()
        return certificate

    def verify_chain(self):
        """Return (is_valid, message, details_list)."""
        if not self.chain:
            return False, 'Blockchain is empty.', []
        details = []
        for i, block in enumerate(self.chain):
            expected = calculate_hash(block)
            hash_ok = block['hash'] == expected
            if i == 0:
                link_ok = block['previous_hash'] == '0'
            else:
                link_ok = block['previous_hash'] == self.chain[i - 1]['hash']
            idx_ok = block['index'] == i
            all_ok = hash_ok and link_ok and idx_ok
            details.append({
                'index': i,
                'hash_valid': hash_ok,
                'link_valid': link_ok,
                'index_valid': idx_ok,
                'all_valid': all_ok,
            })
            if not hash_ok:
                return False, f'Block {i} hash mismatch (data was modified).', details
            if not link_ok:
                return False, f'Block {i} has invalid previous-hash link.', details
            if not idx_ok:
                return False, f'Block {i} has wrong index.', details
        return True, 'All blocks and hash links are valid.', details

    def find_certificate(self, certificate_id):
        target = certificate_id.strip().upper()
        for block in self.chain:
            data = block.get('data', {})
            if data.get('certificate_id', '').upper() == target:
                return block
        return None

    def get_stats(self):
        certs = [b for b in self.chain if 'certificate_id' in b.get('data', {})]
        institutions = {}
        timeline = {}
        for b in certs:
            inst = b['data']['institution']
            institutions[inst] = institutions.get(inst, 0) + 1
            date_key = b['data']['issue_date'][:10]  # YYYY-MM-DD
            timeline[date_key] = timeline.get(date_key, 0) + 1
        valid, msg, _ = self.verify_chain()
        return {
            'total_blocks': len(self.chain),
            'total_certificates': len(certs),
            'chain_valid': valid,
            'chain_message': msg,
            'last_block_time': self.chain[-1]['timestamp'] if self.chain else None,
            'institutions': institutions,
            'timeline': timeline,
        }

    def search(self, query):
        q = query.strip().lower()
        if not q:
            return self.chain
        results = []
        for block in self.chain:
            searchable = json.dumps(block.get('data', {})).lower()
            if q in searchable:
                results.append(block)
        return results

    def get_recent_certificates(self, count=5):
        certs = [b for b in self.chain if 'certificate_id' in b.get('data', {})]
        return list(reversed(certs[-count:]))

blockchain = Blockchain()

@app.route('/')
def dashboard():
    stats = blockchain.get_stats()
    recent = blockchain.get_recent_certificates(5)
    return render_template('dashboard.html',
        active_page='dashboard',
        stats=stats,
        recent_certificates=recent,
        timeline_json=json.dumps(stats['timeline']),
        institutions_json=json.dumps(stats['institutions']),
    )

@app.route('/issue')
def issue_page():
    last_cert = session.pop('last_certificate', None)
    return render_template('issue.html',
        active_page='issue',
        last_certificate=last_cert,
    )

@app.route('/issue', methods=['POST'])
def issue_certificate():
    student_name = request.form.get('student_name', '').strip()
    course = request.form.get('course', '').strip()
    institution = request.form.get('institution', '').strip()
    if not all([student_name, course, institution]):
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('issue_page'))
    if any(len(v) > 150 for v in (student_name, course, institution)):
        flash('Each field must be 150 characters or fewer.', 'error')
        return redirect(url_for('issue_page'))
    cert = blockchain.add_certificate(student_name, course, institution)
    session['last_certificate'] = cert
    flash(f"Certificate issued successfully! ID: {cert['certificate_id']}", 'success')
    return redirect(url_for('issue_page'))

@app.route('/verify')
def verify_page():
    prefill_id = request.args.get('prefill', '')
    return render_template('verify.html', active_page='verify', prefill_id=prefill_id)

@app.route('/verify', methods=['POST'])
def verify_certificate():
    cert_id = request.form.get('certificate_id', '').strip()
    if not cert_id:
        result = {'status': 'NOT_FOUND', 'message': 'Please enter a certificate ID.', 'certificate': None, 'block': None}
    else:
        block = blockchain.find_certificate(cert_id)
        chain_valid, chain_msg, _ = blockchain.verify_chain()
        if block is None:
            result = {'status': 'NOT_FOUND', 'message': 'No certificate found with this ID.', 'certificate': None, 'block': None}
        elif not chain_valid:
            result = {'status': 'WARNING', 'message': f'Certificate found but blockchain integrity failed: {chain_msg}', 'certificate': block['data'], 'block': block}
        else:
            result = {'status': 'VERIFIED', 'message': 'Certificate is authentic and blockchain integrity is confirmed.', 'certificate': block['data'], 'block': block}
    return render_template('verify.html', active_page='verify', result=result)

@app.route('/explorer')
def explorer():
    query = request.args.get('q', '').strip()
    if query:
        blocks = blockchain.search(query)
    else:
        blocks = blockchain.chain
    return render_template('explorer.html',
        active_page='explorer',
        chain=blocks,
        full_chain=blockchain.chain,
        search_query=query,
    )

@app.route('/integrity')
def integrity():
    valid, message, details = blockchain.verify_chain()
    return render_template('integrity.html',
        active_page='integrity',
        chain=blockchain.chain,
        integrity={'valid': valid, 'message': message, 'details': details},
    )

@app.route('/tamper-demo')
def tamper_demo():
    return render_template('tamper_demo.html',
        active_page='tamper',
        chain=blockchain.chain,
    )

@app.route('/certificate/<cert_id>/pdf')
def certificate_pdf(cert_id):
    block = blockchain.find_certificate(cert_id)
    if not block:
        flash('Certificate not found.', 'error')
        return redirect(url_for('verify_page'))
    cert = block['data']
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    # Border
    c.setStrokeColor(HexColor('#14213d'))
    c.setLineWidth(3)
    c.rect(30, 30, width - 60, height - 60)
    c.setLineWidth(1)
    c.rect(40, 40, width - 80, height - 80)
    # Title
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(HexColor('#14213d'))
    c.drawCentredString(width / 2, height - 120, 'Certificate of Completion')
    # Decorative line
    c.setStrokeColor(HexColor('#2563eb'))
    c.setLineWidth(2)
    c.line(width/2 - 100, height - 135, width/2 + 100, height - 135)
    # "This is to certify that"
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#475569'))
    c.drawCentredString(width / 2, height - 180, 'This is to certify that')
    # Student name
    c.setFont('Helvetica-Bold', 24)
    c.setFillColor(HexColor('#1e293b'))
    c.drawCentredString(width / 2, height - 220, cert['student_name'])
    # "has successfully completed"
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#475569'))
    c.drawCentredString(width / 2, height - 260, 'has successfully completed')
    # Course
    c.setFont('Helvetica-Bold', 20)
    c.setFillColor(HexColor('#2563eb'))
    c.drawCentredString(width / 2, height - 295, cert['course'])
    # "from"
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#475569'))
    c.drawCentredString(width / 2, height - 330, 'from')
    # Institution
    c.setFont('Helvetica-Bold', 18)
    c.setFillColor(HexColor('#1e293b'))
    c.drawCentredString(width / 2, height - 365, cert['institution'])
    # Date
    c.setFont('Helvetica', 12)
    c.setFillColor(HexColor('#64748b'))
    c.drawCentredString(width / 2, height - 410, f"Issue Date: {cert['issue_date']}")
    # Certificate ID
    c.setFont('Helvetica', 10)
    c.drawCentredString(width / 2, height - 435, f"Certificate ID: {cert['certificate_id']}")
    # Block hash
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#94a3b8'))
    c.drawCentredString(width / 2, height - 455, f"Block Hash: {block['hash']}")
    # QR Code
    qr_img = qrcode.make(cert['certificate_id'], box_size=4, border=2)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)
    qr_reader = ImageReader(qr_buf)
    c.drawImage(qr_reader, width/2 - 50, 80, 100, 100)
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#94a3b8'))
    c.drawCentredString(width / 2, 65, 'Scan to verify')
    # Blockchain verified badge
    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(HexColor('#16a34a'))
    c.drawCentredString(width / 2, height - 480, '✓ Blockchain Verified')
    c.save()
    buf.seek(0)
    return send_file(buf, mimetype='application/pdf',
                     download_name=f"certificate_{cert_id}.pdf",
                     as_attachment=True)

@app.route('/certificate/<cert_id>/qr')
def certificate_qr(cert_id):
    block = blockchain.find_certificate(cert_id)
    if not block:
        flash('Certificate not found.', 'error')
        return redirect(url_for('verify_page'))
    img = qrcode.make(request.host_url + f'verify?prefill={cert_id}', box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/api/chain')
def api_chain():
    return jsonify(blockchain.chain)

@app.route('/api/issue', methods=['POST'])
def api_issue():
    data = request.get_json(force=True)
    student_name = data.get('student_name', '').strip()
    course = data.get('course', '').strip()
    institution = data.get('institution', '').strip()
    if not all([student_name, course, institution]):
        return jsonify({'error': 'All fields required.'}), 400
    cert = blockchain.add_certificate(student_name, course, institution)
    return jsonify({'certificate': cert, 'block_index': len(blockchain.chain) - 1}), 201

@app.route('/api/verify/<cert_id>')
def api_verify(cert_id):
    block = blockchain.find_certificate(cert_id)
    if not block:
        return jsonify({'status': 'NOT_FOUND', 'message': 'Certificate not found.'}), 404
    valid, msg, _ = blockchain.verify_chain()
    status = 'VERIFIED' if valid else 'WARNING'
    return jsonify({'status': status, 'message': msg, 'certificate': block['data'], 'block': block})

@app.route('/api/stats')
def api_stats():
    return jsonify(blockchain.get_stats())

if __name__ == '__main__':
    app.run(debug=True)