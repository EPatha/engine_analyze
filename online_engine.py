"""Online chess engine using Lichess Cloud Analysis API"""

import requests
import chess


class OnlineEngine:
    """Use Lichess cloud analysis instead of local Stockfish"""
    
    def __init__(self):
        self.api_url = "https://lichess.org/api/cloud-eval"
        
    def analyze_position(self, board):
        """
        Analyze position using Lichess cloud
        
        Args:
            board: chess.Board object
            
        Returns:
            dict: Analysis results
        """
        try:
            fen = board.fen()
            
            # Request cloud analysis
            params = {
                'fen': fen,
                'multiPv': 3
            }
            
            response = requests.get(self.api_url, params=params, timeout=5)
            
            if response.status_code != 200:
                return {'error': 'Cloud analysis unavailable'}
            
            data = response.json()
            
            if 'pvs' not in data or len(data['pvs']) == 0:
                return {'error': 'No analysis available for this position'}
            
            # Get best move from principal variation
            best_pv = data['pvs'][0]
            moves = best_pv.get('moves', '').split()
            
            if not moves:
                return {'error': 'No moves found'}
            
            best_move_uci = moves[0]
            best_move = chess.Move.from_uci(best_move_uci)
            best_move_san = board.san(best_move)
            
            # Get evaluation
            cp = best_pv.get('cp')
            mate = best_pv.get('mate')
            
            if mate is not None:
                evaluation = f"Mate in {mate}"
            elif cp is not None:
                evaluation = f"{cp / 100:.2f}"
            else:
                evaluation = "Unknown"
            
            # Get top moves
            top_moves = []
            for pv in data['pvs'][:3]:
                moves_list = pv.get('moves', '').split()
                if not moves_list:
                    continue
                    
                move_uci = moves_list[0]
                move = chess.Move.from_uci(move_uci)
                move_san = board.san(move)
                
                cp = pv.get('cp')
                mate = pv.get('mate')
                
                if mate is not None:
                    eval_str = f"Mate in {mate}"
                elif cp is not None:
                    eval_str = f"{cp / 100:.2f}"
                else:
                    eval_str = "?"
                
                top_moves.append({
                    'move': move,
                    'move_san': move_san,
                    'move_uci': move_uci,
                    'evaluation': eval_str
                })
            
            return {
                'best_move': best_move,
                'best_move_san': best_move_san,
                'best_move_uci': best_move_uci,
                'evaluation': evaluation,
                'top_moves': top_moves
            }
            
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """No cleanup needed for online engine"""
        pass
