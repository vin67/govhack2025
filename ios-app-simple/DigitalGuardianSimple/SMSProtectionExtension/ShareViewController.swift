import UIKit
import Social
import UniformTypeIdentifiers

class ShareViewController: UIViewController {
    
    @IBOutlet weak var containerView: UIView!
    @IBOutlet weak var titleLabel: UILabel!
    @IBOutlet weak var messagePreviewLabel: UILabel!
    @IBOutlet weak var analysisStatusLabel: UILabel!
    @IBOutlet weak var resultsView: UIView!
    @IBOutlet weak var riskLevelLabel: UILabel!
    @IBOutlet weak var detailsLabel: UILabel!
    @IBOutlet weak var reportButton: UIButton!
    @IBOutlet weak var doneButton: UIButton!
    
    private var messageText: String = ""
    private let analyzer = SMSAnalyzer()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        extractSharedText()
    }
    
    private func setupUI() {
        // Modern iOS design
        view.backgroundColor = UIColor.systemBackground
        
        if containerView == nil {
            // Create UI programmatically if XIB not loaded
            setupProgrammaticUI()
        }
    }
    
    private func setupProgrammaticUI() {
        // Container
        let container = UIView()
        container.backgroundColor = .systemBackground
        container.layer.cornerRadius = 12
        container.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(container)
        
        // Title
        let title = UILabel()
        title.text = "🛡️ Digital Guardian"
        title.font = .systemFont(ofSize: 24, weight: .bold)
        title.textAlignment = .center
        title.translatesAutoresizingMaskIntoConstraints = false
        container.addSubview(title)
        
        // Status
        let status = UILabel()
        status.text = "Analyzing SMS..."
        status.font = .systemFont(ofSize: 16)
        status.textColor = .secondaryLabel
        status.textAlignment = .center
        status.translatesAutoresizingMaskIntoConstraints = false
        container.addSubview(status)
        
        // Message preview
        let preview = UILabel()
        preview.font = .systemFont(ofSize: 14)
        preview.textColor = .label
        preview.numberOfLines = 3
        preview.translatesAutoresizingMaskIntoConstraints = false
        container.addSubview(preview)
        
        // Results container
        let results = UIView()
        results.backgroundColor = .secondarySystemBackground
        results.layer.cornerRadius = 8
        results.isHidden = true
        results.translatesAutoresizingMaskIntoConstraints = false
        container.addSubview(results)
        
        // Risk level
        let risk = UILabel()
        risk.font = .systemFont(ofSize: 20, weight: .semibold)
        risk.textAlignment = .center
        risk.translatesAutoresizingMaskIntoConstraints = false
        results.addSubview(risk)
        
        // Details
        let details = UILabel()
        details.font = .systemFont(ofSize: 14)
        details.textColor = .secondaryLabel
        details.numberOfLines = 0
        details.translatesAutoresizingMaskIntoConstraints = false
        results.addSubview(details)
        
        // Buttons stack
        let buttonStack = UIStackView()
        buttonStack.axis = .horizontal
        buttonStack.distribution = .fillEqually
        buttonStack.spacing = 12
        buttonStack.translatesAutoresizingMaskIntoConstraints = false
        container.addSubview(buttonStack)
        
        // Report button
        let report = UIButton(type: .system)
        report.setTitle("Report Scam", for: .normal)
        report.backgroundColor = .systemRed
        report.setTitleColor(.white, for: .normal)
        report.layer.cornerRadius = 8
        report.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        report.addTarget(self, action: #selector(reportScam), for: .touchUpInside)
        report.isHidden = true
        buttonStack.addArrangedSubview(report)
        
        // Done button
        let done = UIButton(type: .system)
        done.setTitle("Done", for: .normal)
        done.backgroundColor = .systemBlue
        done.setTitleColor(.white, for: .normal)
        done.layer.cornerRadius = 8
        done.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        done.addTarget(self, action: #selector(done(_:)), for: .touchUpInside)
        buttonStack.addArrangedSubview(done)
        
        // Store references
        self.containerView = container
        self.titleLabel = title
        self.analysisStatusLabel = status
        self.messagePreviewLabel = preview
        self.resultsView = results
        self.riskLevelLabel = risk
        self.detailsLabel = details
        self.reportButton = report
        self.doneButton = done
        
        // Constraints
        NSLayoutConstraint.activate([
            container.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            container.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            container.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            container.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            title.topAnchor.constraint(equalTo: container.topAnchor, constant: 20),
            title.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 20),
            title.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -20),
            
            status.topAnchor.constraint(equalTo: title.bottomAnchor, constant: 8),
            status.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 20),
            status.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -20),
            
            preview.topAnchor.constraint(equalTo: status.bottomAnchor, constant: 16),
            preview.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 20),
            preview.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -20),
            
            results.topAnchor.constraint(equalTo: preview.bottomAnchor, constant: 16),
            results.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 20),
            results.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -20),
            
            risk.topAnchor.constraint(equalTo: results.topAnchor, constant: 12),
            risk.leadingAnchor.constraint(equalTo: results.leadingAnchor, constant: 12),
            risk.trailingAnchor.constraint(equalTo: results.trailingAnchor, constant: -12),
            
            details.topAnchor.constraint(equalTo: risk.bottomAnchor, constant: 8),
            details.leadingAnchor.constraint(equalTo: results.leadingAnchor, constant: 12),
            details.trailingAnchor.constraint(equalTo: results.trailingAnchor, constant: -12),
            details.bottomAnchor.constraint(equalTo: results.bottomAnchor, constant: -12),
            
            buttonStack.topAnchor.constraint(equalTo: results.bottomAnchor, constant: 20),
            buttonStack.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 20),
            buttonStack.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -20),
            buttonStack.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -20),
            buttonStack.heightAnchor.constraint(equalToConstant: 44)
        ])
    }
    
    private func extractSharedText() {
        guard let extensionItem = extensionContext?.inputItems.first as? NSExtensionItem,
              let itemProvider = extensionItem.attachments?.first else {
            showError("No text found")
            return
        }
        
        if itemProvider.hasItemConformingToTypeIdentifier(UTType.text.identifier) {
            itemProvider.loadItem(forTypeIdentifier: UTType.text.identifier, options: nil) { [weak self] (text, error) in
                DispatchQueue.main.async {
                    if let sharedText = text as? String {
                        self?.messageText = sharedText
                        self?.messagePreviewLabel.text = sharedText
                        self?.analyzeSMS(sharedText)
                    } else {
                        self?.showError("Could not extract text")
                    }
                }
            }
        }
    }
    
    private func analyzeSMS(_ text: String) {
        analysisStatusLabel.text = "🔍 Checking against database..."
        
        // Analyze the SMS
        let result = analyzer.analyze(message: text)
        
        // Show results
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            self?.showResults(result)
        }
    }
    
    private func showResults(_ result: SMSAnalysisResult) {
        analysisStatusLabel.text = "Analysis Complete"
        resultsView.isHidden = false
        
        switch result.riskLevel {
        case .safe:
            riskLevelLabel.text = "✅ SAFE"
            riskLevelLabel.textColor = .systemGreen
            detailsLabel.text = result.details
            reportButton.isHidden = true
            resultsView.backgroundColor = UIColor.systemGreen.withAlphaComponent(0.1)
            
        case .threat:
            riskLevelLabel.text = "🚨 SCAM DETECTED"
            riskLevelLabel.textColor = .systemRed
            detailsLabel.text = result.details
            reportButton.isHidden = false
            resultsView.backgroundColor = UIColor.systemRed.withAlphaComponent(0.1)
            
        case .suspicious:
            riskLevelLabel.text = "⚠️ SUSPICIOUS"
            riskLevelLabel.textColor = .systemOrange
            detailsLabel.text = result.details
            reportButton.isHidden = false
            resultsView.backgroundColor = UIColor.systemOrange.withAlphaComponent(0.1)
            
        case .unknown:
            riskLevelLabel.text = "❓ UNKNOWN"
            riskLevelLabel.textColor = .systemGray
            detailsLabel.text = result.details
            reportButton.isHidden = true
            resultsView.backgroundColor = UIColor.systemGray.withAlphaComponent(0.1)
        }
    }
    
    private func showError(_ message: String) {
        analysisStatusLabel.text = message
        analysisStatusLabel.textColor = .systemRed
    }
    
    @objc private func reportScam() {
        // Save to local database for future protection
        analyzer.reportScam(message: messageText)
        
        // Show confirmation
        let alert = UIAlertController(title: "Scam Reported", message: "Thank you for helping protect the community!", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
            self.done(nil)
        })
        present(alert, animated: true)
    }
    
    @objc private func done(_ sender: Any?) {
        self.extensionContext?.completeRequest(returningItems: nil, completionHandler: nil)
    }
}