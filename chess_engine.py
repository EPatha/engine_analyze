"""Stockfish chess engine integration for position analysis"""

import chess
import chess.engine
import config
import os


class ChessEngine:
    """Wrapper for Stockfish chess engine"""
    
    def __init__(self, stockfish_path=None):
        """
        Initialize chess engine
        
        Args:
            stockfish_path: Path to Stockfish executable
        """
        self.stockfish_path = stockfish_path or config.STOCKFISH_PATH
        self.engine = None
        
        # Try to initialize engine
        self.initialize_engine()
        
    def initialize_engine(self):
        """Initialize Stockfish engine"""
        if not os.path.exists(self.stockfish_path):
            print(f"Warning: Stockfish not found at {self.stockfish_path}")
            print("Please install Stockfish:")
            print("  macOS: brew install stockfish")
            print("  Or download from: https://stockfishchess.org/download/")
            return False
            
        try:
            # Use python-chess engine interface
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            print(f"Stockfish engine initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            return False
    
    def analyze_position(self, board):
        """
        Analyze chess position and get best move
        
        Args:
            board: chess.Board object
            
        Returns:
            dict: Analysis results with best move, evaluation, and variations
        """
        if not self.engine:
            return {
                'error': 'Engine not initialized',
                'best_move': None,
                'evaluation': None
            }
        
        try:
            # Analyze position with multipv to get top 3 moves at once
            info_list = self.engine.analyse(
                board, 
                chess.engine.Limit(
                    depth=config.STOCKFISH_DEPTH,
                    time=config.STOCKFISH_TIME_LIMIT
                ),
                multipv=3  # Get top 3 moves
            )
            
            # Handle both single and multiple PV results
            if not isinstance(info_list, list):
                info_list = [info_list]
            
            if not info_list or not info_list[0].get('pv'):
                return {
                    'error': 'No analysis available',
                    'best_move': None,
                    'evaluation': None
                }
            
            # Get best move from first analysis
            best_info = info_list[0]
            best_move = best_info['pv'][0]
            
            # Get evaluation score
            score = best_info.get('score')
            if score:
                # Convert score to centipawns
                if score.is_mate():
                    eval_str = f"Mate in {score.relative.moves}"
                else:
                    centipawns = score.relative.score()
                    eval_str = f"{centipawns / 100:.2f}"
            else:
                eval_str = "Unknown"
            
            # Get principal variation (best line)
            pv = best_info.get('pv', [])
            pv_str = ' '.join([move.uci() for move in pv[:5]])  # First 5 moves
            
            # Collect top moves
            top_moves = []
            for analysis in info_list:
                pv = analysis.get('pv', [])
                if not pv:
                    continue
                    
                move = pv[0]
                score = analysis.get('score')
                
                if score:
                    if score.is_mate():
                        eval_str_move = f"Mate in {score.relative.moves}"
                    else:
                        centipawns = score.relative.score()
                        eval_str_move = f"{centipawns / 100:.2f}"
                else:
                    eval_str_move = "Unknown"
                
                top_moves.append({
                    'move': move,
                    'move_san': board.san(move),
                    'move_uci': move.uci(),
                    'evaluation': eval_str_move,
                    'pv': ' '.join([m.uci() for m in pv[:3]])
                })
            
            return {
                'best_move': best_move,
                'best_move_san': board.san(best_move),
                'best_move_uci': best_move.uci(),
                'evaluation': eval_str,
                'principal_variation': pv_str,
                'depth': best_info.get('depth', 0),
                'nodes': best_info.get('nodes', 0),
                'top_moves': top_moves
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'best_move': None,
                'evaluation': None
            }
    
    def get_top_moves(self, board, num_moves=3):
        """
        Get multiple top moves with evaluations
        
        Args:
            board: chess.Board object
            num_moves: Number of top moves to return
            
        Returns:
            list: List of move analysis dictionaries
        """
        if not self.engine:
            return []
        
        try:
            # Analyze with multipv
            info = self.engine.analyse(
                board,
                chess.engine.Limit(
                    depth=config.STOCKFISH_DEPTH,
                    time=config.STOCKFISH_TIME_LIMIT
                ),
                multipv=num_moves
            )
            
            top_moves = []
            
            # Handle both single and multiple PV results
            if not isinstance(info, list):
                info = [info]
            
            for analysis in info:
                pv = analysis.get('pv', [])
                if not pv:
                    continue
                    
                move = pv[0]
                score = analysis.get('score')
                
                if score:
                    if score.is_mate():
                        eval_str = f"Mate in {score.relative.moves}"
                    else:
                        centipawns = score.relative.score()
                        eval_str = f"{centipawns / 100:.2f}"
                else:
                    eval_str = "Unknown"
                
                top_moves.append({
                    'move': move,
                    'move_san': board.san(move),
                    'move_uci': move.uci(),
                    'evaluation': eval_str,
                    'pv': ' '.join([m.uci() for m in pv[:3]])
                })
            
            return top_moves
            
        except Exception as e:
            print(f"Error getting top moves: {e}")
            return []
    
    def close(self):
        """Clean up engine resources"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
