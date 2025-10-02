import os
import platform
import sys
from collections import defaultdict

class DiskAnalyzer:
    def __init__(self):
        self.system = platform.system()
    
    def install_requirements(self):
        """Automatically install required packages"""
        try:
            if self.system == "Windows":
                # For Windows, we might need win32api for disk info
                import subprocess
                try:
                    import win32api
                except ImportError:
                    print("Installing pywin32...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
            else:
                # Linux/Mac - no special requirements needed
                pass
        except Exception as e:
            print(f"Warning: Could not auto-install requirements: {e}")
    
    def get_directory_size(self, path):
        """Calculate total size of directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
        except PermissionError:
            print(f"Permission denied accessing: {path}")
        
        return total_size
    
    def get_detailed_analysis(self, path, top_n=20):
        """Get detailed analysis of disk space usage"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        print(f"\n{'='*80}")
        print(f"Detailed Disk Space Analysis for: {os.path.abspath(path)}")
        print(f"{'='*80}")
        
        # Get total size
        total_size = self.get_directory_size(path)
        print(f"Total Size: {self.human_readable_size(total_size)}")
        print(f"Path: {os.path.abspath(path)}")
        print()
        
        # Analyze directories and files
        dir_sizes = defaultdict(int)
        file_sizes = []
        
        try:
            for root, dirs, files in os.walk(path):
                # Calculate directory size
                dir_total = 0
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                        dir_total += size
                        file_sizes.append((fp, size))
                    except (OSError, FileNotFoundError):
                        continue
                
                # Store directory sizes (excluding root)
                if root != path:
                    dir_sizes[root] = dir_total
        
        except PermissionError:
            print("Permission denied while walking directory tree")
        
        # Sort and display top directories
        sorted_dirs = sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)
        print(f"Top {min(top_n, len(sorted_dirs))} Largest Directories:")
        print("-" * 60)
        for i, (dir_path, size) in enumerate(sorted_dirs[:top_n]):
            print(f"{i+1:2d}. {self.human_readable_size(size):>12} - {os.path.basename(dir_path)}")
        
        # Sort and display top files
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        print(f"\nTop {min(top_n, len(file_sizes))} Largest Files:")
        print("-" * 60)
        for i, (file_path, size) in enumerate(file_sizes[:top_n]):
            print(f"{i+1:2d}. {self.human_readable_size(size):>12} - {os.path.basename(file_path)}")
        
        # File type distribution
        file_types = defaultdict(int)
        file_counts = defaultdict(int)
        
        for file_path, size in file_sizes:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if not ext:
                    ext = "no_extension"
                file_types[ext] += size
                file_counts[ext] += 1
            except Exception:
                continue
        
        print(f"\nFile Type Distribution:")
        print("-" * 60)
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        for ext, size in sorted_types[:15]:
            count = file_counts[ext]
            percentage = (size / total_size) * 100 if total_size > 0 else 0
            print(f"{ext:>15}: {self.human_readable_size(size):>12} ({count:4d} files) - {percentage:.1f}%")
        
        # Summary statistics
        print(f"\nSummary Statistics:")
        print("-" * 60)
        print(f"Total Files: {len(file_sizes):,}")
        print(f"Total Directories: {len(sorted_dirs):,}")
        print(f"Average File Size: {self.human_readable_size(total_size / max(len(file_sizes), 1)) if file_sizes else 'N/A'}")
        
        # Find largest subdirectories
        self.find_largest_subdirs(path, top_n)
        
        return {
            'total_size': total_size,
            'file_count': len(file_sizes),
            'dir_count': len(sorted_dirs),
            'largest_dirs': sorted_dirs[:top_n],
            'largest_files': file_sizes[:top_n],
            'file_types': dict(sorted_types)
        }
    
    def find_largest_subdirs(self, path, top_n=10):
        """Find the largest subdirectories"""
        print(f"\nLargest Subdirectories (within {os.path.basename(path)}):")
        print("-" * 60)
        
        # Get all subdirectories
        subdirs = []
        try:
            for root, dirs, files in os.walk(path):
                if root != path:  # Skip the main directory
                    size = self.get_directory_size(root)
                    subdirs.append((root, size))
        except Exception as e:
            print(f"Error analyzing subdirectories: {e}")
        
        # Sort and display
        subdirs.sort(key=lambda x: x[1], reverse=True)
        for i, (dir_path, size) in enumerate(subdirs[:top_n]):
            print(f"{i+1:2d}. {self.human_readable_size(size):>12} - {os.path.basename(dir_path)}")
    
    def human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_system_info(self):
        """Get system information"""
        print(f"\n{'='*80}")
        print("System Information")
        print(f"{'='*80}")
        print(f"Operating System: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")
        print(f"Python Version: {sys.version}")
        
        # Get disk usage
        try:
            if self.system == "Windows":
                import shutil
                drives = []
                try:
                    import win32api
                    drive_list = win32api.GetLogicalDriveStrings()
                    drive_list = drive_list.split('\000')[:-1]
                    for drive in drive_list:
                        try:
                            total, used, free = win32api.GetDiskFreeSpaceEx(drive)
                            drives.append((drive, total, used, free))
                        except Exception as e:
                            print(f"Could not get info for drive {drive}: {e}")
                except ImportError:
                    # Fallback to shutil if win32api is not available
                    print("win32api not available, using basic disk info...")
                
                if drives:
                    for drive, total, used, free in drives:
                        print(f"Drive {drive}: Total: {self.human_readable_size(total)}, Used: {self.human_readable_size(used)}, Free: {self.human_readable_size(free)}")
            else:
                import shutil
                try:
                    total, used, free = shutil.disk_usage('/')
                    print(f"Root filesystem: Total: {self.human_readable_size(total)}, Used: {self.human_readable_size(used)}, Free: {self.human_readable_size(free)}")
                except Exception as e:
                    print(f"Could not get disk usage info: {e}")
        except Exception as e:
            print(f"Error getting system info: {e}")
    
    def run_analysis(self):
        """Main analysis function"""
        self.get_system_info()
        
        while True:
            try:
                print("\n" + "="*80)
                path = input("Enter the directory path to analyze (or 'quit' to exit): ").strip()
                
                if path.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not path:
                    print("Please enter a valid path.")
                    continue
                
                # Check if path exists
                if not os.path.exists(path):
                    print(f"Error: Path does not exist: {path}")
                    continue
                
                if not os.path.isdir(path):
                    print(f"Error: Path is not a directory: {path}")
                    continue
                
                # Get analysis
                result = self.get_detailed_analysis(path)
                
                print("\nAnalysis complete!")
                
            except KeyboardInterrupt:
                print("\n\nAnalysis interrupted by user.")
                break
            except Exception as e:
                print(f"Error during analysis: {e}")
                continue
            
            # Ask if user wants to analyze another path
            try:
                choice = input("\nWould you like to analyze another directory? (y/n): ").strip().lower()
                if choice not in ['y', 'yes']:
                    print("Goodbye!")
                    break
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

def main():
    """Main function"""
    try:
        analyzer = DiskAnalyzer()
        analyzer.run_analysis()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
