from http.server import BaseHTTPRequestHandler
from orchestrator import Orchestrator, IdeaRequest, RefinementRequest
import json
from urllib.parse import parse_qs

orchestrator = Orchestrator()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        try:
            if self.path == '/api/process':
                result = orchestrator.process_initial_idea(data['idea'])
                response = result
            elif self.path == '/api/refine':
                result = orchestrator.refine_content(data['refinement'])
                response = result
            elif self.path == '/api/finalize':
                blog_post = orchestrator.finalize_to_blog()
                response = {"blog_post": blog_post}
            else:
                self.send_error(404)
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())